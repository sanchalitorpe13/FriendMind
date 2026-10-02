import json
import ollama


def generate_quiz(context, num_questions=5, difficulty="Medium"):

    # Keep the context reasonably small for faster generation
    context = context[:6000]

    prompt = f"""
You are creating a Python study quiz from the study material below.

Difficulty: {difficulty}

STRICT RULES:
1. Generate exactly {num_questions} questions.
2. Each question must have exactly 4 options.
3. Only ONE option can be correct.
4. The "answer" MUST be the exact text of the correct option.
5. The answer MUST appear exactly in the options list.
6. Use ONLY information from the study material.
7. Keep questions and options short.
8. Do not include explanations.
9. Return ONLY valid JSON.
10. Do not use markdown or code fences.

Study material:
----------------
{context}
----------------

Return exactly this structure:

{{
  "questions": [
    {{
      "question": "Question text",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "answer": "Option B"
    }}
  ]
}}
"""

    try:

        response = ollama.chat(
            model="gemma3:4b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.1,
                "num_predict": 800
            }
        )

        content = response["message"]["content"].strip()

        # Remove accidental markdown fences
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

        quiz = json.loads(content)

        if "questions" not in quiz:
            return {
                "error": "Quiz response did not contain questions."
            }

        valid_questions = []

        for question in quiz["questions"]:

            # Check required fields
            if not all(
                key in question
                for key in ["question", "options", "answer"]
            ):
                continue

            options = question["options"]
            answer = question["answer"]

            # Must have exactly 4 options
            if len(options) != 4:
                continue

            # Answer must exactly match one option
            if answer not in options:
                continue

            # Add explanation ourselves
            question["explanation"] = (
                f"The correct answer is **{answer}**."
            )

            valid_questions.append(question)

        # Make sure we have enough valid questions
        if len(valid_questions) < num_questions:

            return {
                "error": (
                    f"Gemma generated only "
                    f"{len(valid_questions)} valid questions "
                    f"out of {num_questions}."
                )
            }

        # Keep exactly the requested number
        valid_questions = valid_questions[:num_questions]

        return {
            "questions": valid_questions
        }

    except json.JSONDecodeError:

        return {
            "error": "Gemma returned invalid JSON.",
            "raw_response": content
        }

    except Exception as e:

        return {
            "error": f"Quiz generation failed: {str(e)}"
        }