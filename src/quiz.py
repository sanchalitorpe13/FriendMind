import json
import ollama


def generate_quiz(context, num_questions=5, difficulty="Medium"):
    """
    Generate a multiple-choice quiz using only the provided study material.
    """

    prompt = f"""
You are FriendMind, a personal AI study assistant.

Create a multiple-choice quiz using ONLY the study material provided below.

Study material:
----------------
{context}
----------------

Requirements:
- Generate exactly {num_questions} questions.
- Difficulty: {difficulty}
- Each question must have exactly 4 options.
- Only ONE option must be correct.
- Questions must be answerable from the study material.
- Do not invent information.
- Include a short explanation for the correct answer.

Return ONLY valid JSON in this exact format:

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
            "answer": 0,
            "explanation": "Short explanation"
        }}
    ]
}}
"""

    response = ollama.chat(
        model="gemma3:4b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"]

    # Remove possible Markdown code fences
    content = content.replace("```json", "").replace("```", "").strip()

    try:
        quiz = json.loads(content)
        return quiz

    except json.JSONDecodeError:
        return {
            "error": "Could not generate a valid quiz.",
            "raw_response": content
        }