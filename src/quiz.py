import json
import re
import ollama


MODEL = "gemma3:4b"


def _clean_json(content):
    """Remove accidental Markdown code fences from model output."""
    content = content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    return content


def _is_good_question_text(question):
    """
    Reject obvious statement-style or malformed questions.

    A multiple-choice question should normally either:
    - end with '?', or
    - use a recognizable question structure.
    """

    question = question.strip()

    if not question:
        return False

    lower = question.lower()

    # Reject explicit True/False style wording.
    if lower.startswith(("true or false", "is it true", "true/false")):
        return False

    # Reject questions that are clearly just statements.
    question_words = [
        "what",
        "which",
        "who",
        "where",
        "when",
        "why",
        "how",
        "is ",
        "are ",
        "does ",
        "do ",
        "can ",
        "will ",
        "which ",
        "identify ",
        "select ",
        "choose ",
        "what is ",
        "what are ",
        "which operator",
        "which of"
    ]

    looks_like_question = (
        "?" in question
        or any(lower.startswith(word) for word in question_words)
    )

    if not looks_like_question:
        return False

    # Reject extremely long generated paragraphs.
    if len(question) > 350:
        return False

    return True


def _validate_questions(questions, num_questions):
    """
    Structural validation.

    IMPORTANT:
    This function never changes the generated question.
    It only accepts or rejects it.
    """

    if not isinstance(questions, list):
        return []

    valid_questions = []
    seen_questions = set()

    for question in questions:

        if not isinstance(question, dict):
            continue

        required_keys = [
            "question",
            "options",
            "answer"
        ]

        if not all(key in question for key in required_keys):
            continue

        question_text = str(
            question["question"]
        ).strip()

        answer = str(
            question["answer"]
        ).strip()

        options = question["options"]

        if not question_text:
            continue

        # Reject malformed/statement-style questions.
        if not _is_good_question_text(question_text):
            continue

        if not isinstance(options, list):
            continue

        # Exactly four options.
        if len(options) != 4:
            continue

        options = [
            str(option).strip()
            for option in options
        ]

        # No empty options.
        if any(not option for option in options):
            continue

        # No duplicate options.
        if len(
            set(option.lower() for option in options)
        ) != 4:
            continue

        # Reject True/False style options.
        normalized_options = {
            option.lower()
            for option in options
        }

        if normalized_options == {
            "true",
            "false"
        }:
            continue

        # Reject questions where answer is True/False.
        if answer.lower() in {"true", "false"}:
            continue

        # Answer must exactly match one option.
        if answer not in options:
            continue

        # Prevent duplicate questions.
        question_key = re.sub(
            r"\s+",
            " ",
            question_text.lower()
        )

        if question_key in seen_questions:
            continue

        seen_questions.add(question_key)

        # Preserve the original generated question exactly.
        valid_questions.append(
            {
                "question": question_text,
                "options": options,
                "answer": answer
            }
        )

        if len(valid_questions) >= num_questions:
            break

    return valid_questions


def _verify_questions(context, questions):
    """
    Semantic verification layer.

    The verifier ONLY decides whether each question is valid.

    It is NOT allowed to:
    - rewrite questions
    - rewrite options
    - change answers
    - create new questions
    - convert questions into True/False questions

    It returns the ORIGINAL questions that passed verification.
    """

    if not questions:
        return []

    questions_json = json.dumps(
        questions,
        ensure_ascii=False,
        indent=2
    )

    verification_prompt = f"""
You are the factual quality-control system for FriendMind.

Your task is ONLY to verify the multiple-choice questions below
against the supplied study material.

You are NOT a quiz generator.

You MUST NOT:
- rewrite any question
- rewrite any option
- change any answer
- create new questions
- convert a question into True/False
- change the order of options
- use outside knowledge

For each question, decide whether the ORIGINAL question is
supported by the study material.

A question is VALID only if:

1. The question is supported by the study material.
2. The listed correct answer is supported by the study material.
3. The correct answer actually answers the question.
4. Exactly one option is correct.
5. The question is clear and unambiguous.
6. The question does not mix different concepts.
7. The question does not contain a contradiction.
8. The question is actually a multiple-choice question.
9. The question does not incorrectly describe another concept.

Pay special attention to similar Python concepts:

- Membership operators: in, not in
- Identity operators: is, is not
- Equality: ==, !=
- Assignment: =
- Logical operators: and, or, not
- Bitwise operators: &, |, ^, ~, <<, >>

For example, if a question asks about membership operators,
do not approve an answer that describes identity operators.

IMPORTANT:

If you are uncertain, mark the question INVALID.

Do not try to repair the question.

STUDY MATERIAL
====================
{context}
====================

ORIGINAL GENERATED QUESTIONS
====================
{questions_json}
====================

Return ONLY valid JSON.

Use this exact format:

{{
    "verifications": [
        {{
            "index": 0,
            "valid": true
        }},
        {{
            "index": 1,
            "valid": false
        }}
    ]
}}

Rules:

- Include exactly one verification object for every question.
- "index" must refer to the original question position.
- "valid" must be either true or false.
- Do not include rewritten questions.
- Do not include replacement answers.
- Do not include explanations.
- Do not use Markdown.
"""

    try:

        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": verification_prompt
                }
            ],
            options={
                "temperature": 0.0,
                "num_predict": 1000
            }
        )

        content = _clean_json(
            response["message"]["content"]
        )

        verification = json.loads(content)

        verifications = verification.get(
            "verifications",
            []
        )

        if not isinstance(verifications, list):
            return []

        valid_indexes = set()

        for item in verifications:

            if not isinstance(item, dict):
                continue

            index = item.get("index")
            valid = item.get("valid")

            if not isinstance(index, int):
                continue

            if valid is True:
                valid_indexes.add(index)

        # IMPORTANT:
        # Return the ORIGINAL questions.
        # Never use anything generated by the verifier
        # to modify them.
        verified_questions = []

        for index, question in enumerate(questions):

            if index in valid_indexes:
                verified_questions.append(question)

        return verified_questions

    except Exception:
        # Fail closed.
        # If semantic verification fails, do not show
        # potentially unreliable questions.
        return []


def generate_quiz(
    context,
    num_questions=5,
    difficulty="Medium"
):
    """
    Generate a grounded multiple-choice quiz.

    Pipeline:

        Retrieved study material
                ↓
        Gemma generates MCQs
                ↓
        Structural validation
                ↓
        Semantic verification
                ↓
        Final validated MCQs
    """

    try:
        num_questions = int(num_questions)
    except (TypeError, ValueError):
        num_questions = 5

    # Keep quiz size reasonable.
    num_questions = max(
        1,
        min(num_questions, 10)
    )

    context = str(context).strip()

    if not context:
        return {
            "error": "No study material was provided."
        }

    # Limit context sent to the model.
    context = context[:7000]

    # Generate extra questions because some may be rejected.
    requested_questions = num_questions + 5

    prompt = f"""
You are FriendMind, an AI study companion.

Create a multiple-choice quiz ONLY from the study material below.

Difficulty: {difficulty}

Generate exactly {requested_questions} candidate questions.

STRICT RULES:

1. Every question must have exactly 4 options.
2. Exactly ONE option must be correct.
3. The "answer" must be the exact text of the correct option.
4. The answer MUST appear in the options list.
5. Use ONLY information from the study material.
6. Do NOT use outside knowledge.
7. Do NOT invent facts.
8. Do NOT create True/False questions.
9. Do NOT use True/False as the four options.
10. Every question must be a genuine multiple-choice question.
11. Every question must be clearly worded.
12. Do not write statements as questions.
13. Do not mix different concepts.
14. Do not confuse similar concepts.
15. Do not repeat questions.
16. Do not unnecessarily repeat the same concept.
17. Keep questions concise.
18. Keep options concise.
19. Return ONLY valid JSON.
20. Do not use Markdown.
21. Do not use code fences.
22. Do not include explanations.

IMPORTANT PYTHON CONCEPTS:

Keep these concepts separate:

Membership:
- in
- not in

Identity:
- is
- is not

Equality:
- ==
- !=

Assignment:
- =

Logical:
- and
- or
- not

Bitwise:
- &
- |
- ^
- ~
- <<
- >>

Do not use the definition of one concept as the answer to a
question about another concept.

STUDY MATERIAL
========================
{context}
========================

Return exactly:

{{
    "questions": [
        {{
            "question": "What does the membership operator 'in' check?",
            "options": [
                "Whether a value is present in a sequence",
                "Whether two objects have the same identity",
                "Whether a value is assigned to a variable",
                "Whether two numbers are equal"
            ],
            "answer": "Whether a value is present in a sequence"
        }}
    ]
}}
"""

    for attempt in range(3):

        try:

            response = ollama.chat(
                model=MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0.0,
                    "num_predict": 1800
                }
            )

            content = _clean_json(
                response["message"]["content"]
            )

            quiz = json.loads(content)

            if not isinstance(quiz, dict):
                continue

            generated_questions = quiz.get(
                "questions",
                []
            )

            # -----------------------------------------
            # PASS 1: STRUCTURAL VALIDATION
            # -----------------------------------------

            structurally_valid = _validate_questions(
                generated_questions,
                requested_questions
            )

            if len(structurally_valid) < num_questions:
                continue

            # -----------------------------------------
            # PASS 2: SEMANTIC VERIFICATION
            # -----------------------------------------

            verified_questions = _verify_questions(
                context,
                structurally_valid
            )

            if len(verified_questions) < num_questions:
                continue

            # -----------------------------------------
            # FINAL VALIDATION
            # -----------------------------------------

            final_questions = _validate_questions(
                verified_questions,
                num_questions
            )

            if len(final_questions) != num_questions:
                continue

            return {
                "questions": final_questions
            }

        except json.JSONDecodeError:
            continue

        except Exception as e:

            if attempt == 2:
                return {
                    "error": (
                        f"Quiz generation failed: {str(e)}"
                    )
                }

    return {
        "error": (
            "Could not generate enough reliable "
            "multiple-choice questions from the "
            "uploaded study material. "
            "Please try generating the quiz again."
        )
    }