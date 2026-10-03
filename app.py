from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pypdf import PdfReader
import ollama
import json
import tempfile
import os
from src.rag import add_document, search_documents, get_indexed_documents
from src.quiz import generate_quiz


# ============================================================
# FRIENDMIND API
# ============================================================

app = FastAPI(
    title="FriendMind API",
    description="AI-powered personal study companion",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DOCUMENT STATE
# ============================================================
@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return {"success": False, "error": "Only PDF files are supported."}

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_path = temp_file.name

        text = extract_pdf_text(temp_path)

        if not text.strip():
            return {
                "success": False,
                "error": "Could not extract text from this PDF."
            }

        chunk_count = add_document(
            text,
            document_name=file.filename
        )

        return {
            "success": True,
            "filename": file.filename,
            "chunks": chunk_count,
            "characters": len(text),
            "message": "PDF uploaded and indexed successfully."
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)



# ============================================================
# SERVE INDEX.HTML
# ============================================================

@app.get("/")
def serve_frontend():
    return FileResponse("index.html")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():
    documents = get_indexed_documents()

    return {
        "status": "healthy",
        "model": "gemma3:4b",
        "documents": len(documents)
    }


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_pdf_text(file_path):
    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


# ============================================================
# UPLOAD PDF
# ============================================================

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        return {
            "success": False,
            "error": "Only PDF files are supported."
        }

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            contents = await file.read()
            temp_file.write(contents)

            temp_path = temp_file.name

        # Extract PDF text
        reader = PdfReader(temp_path)
        pages = len(reader.pages)
        text = extract_pdf_text(temp_path)

        if not text.strip():
            return {
                "success": False,
                "error": "Could not extract text from this PDF."
            }

        # Add document to ChromaDB
        chunk_count = add_document(
            text,
            document_name=file.filename
        )

        uploaded_documents.append({
            "name": file.filename,
            "chunks": chunk_count
        })

        return {
            "success": True,
            "filename": file.filename,
            "pages": pages,
            "chunks": chunk_count,
            "characters": len(text),
            "message": "PDF uploaded and indexed successfully."
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# ============================================================
# ASK QUESTION
# ============================================================

@app.post("/api/ask")
async def ask_question(data: dict):

    question = data.get("question", "").strip()

    if not question:
        return {
            "success": False,
            "error": "Question is required."
        }

    try:

        results = search_documents(
            question,
            top_k=3
        )

        documents = results.get(
            "documents",
            [[]]
        )[0]

        if not documents:

            return {
                "success": False,
                "error": "No relevant study material found."
            }

        context = "\n\n".join(documents)
        context = context[:7000]

        prompt = f"""
You are FriendMind, a personal AI study companion.

Answer the student's question using ONLY the study material provided below.

Rules:
1. Use only the provided study material.
2. If the answer is not present, say that it is not available in the uploaded material.
3. Give a clear and student-friendly explanation.
4. Do not invent facts.
5. Keep the answer concise but useful.

Study material:
----------------
{context}
----------------

Student question:
{question}
"""

        response = ollama.chat(
            model="gemma3:4b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.2,
                "num_predict": 500
            }
        )

        answer = response["message"]["content"].strip()

        return {
            "success": True,
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "text": doc[:500]
                }
                for doc in documents
            ]
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# GENERATE QUIZ
# ============================================================

# ============================================================
# GENERATE QUIZ
# ============================================================

@app.post("/api/quiz")
async def create_quiz(data: dict):

    num_questions = data.get(
        "num_questions",
        5
    )

    difficulty = data.get(
        "difficulty",
        "Medium"
    )

    try:

        results = search_documents(
            "important concepts definitions examples questions",
            top_k=3
        )

        documents = results.get(
            "documents",
            [[]]
        )[0]

        if not documents:

            return {
                "success": False,
                "error": "Please upload study material first."
            }

        context = "\n\n".join(documents)

        quiz = generate_quiz(
            context=context,
            num_questions=int(num_questions),
            difficulty=difficulty
        )

        if "error" in quiz:

            return {
                "success": False,
                "error": quiz["error"]
            }

        return {
            "success": True,
            "questions": quiz["questions"],
            "quiz": quiz
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# WEAK TOPIC DETECTION
# ============================================================

@app.post("/api/weak-topics")
async def weak_topics(data: dict):
    # Accept the format currently sent by index.html
    results = data.get("incorrect", data.get("results", []))

    if not results:
        return {
            "success": True,
            "analysis": {
                "weak_topics": [],
                "revision_advice": [
                    "You answered all questions correctly. Keep practicing to retain the concepts."
                ]
            }
        }

    try:
        result_text = json.dumps(results, indent=2)

        prompt = f"""
You are an AI study coach.

Analyze the student's incorrect quiz answers below.

Your task:
1. Identify the specific concepts/topics the student struggled with.
2. Identify what concept needs revision based ONLY on the quiz questions and answers.
3. Give short, practical revision advice.

IMPORTANT RULES:
- Use ONLY the information contained in the quiz results.
- Do not invent topics that are not supported by the questions.
- Keep the response concise.
- Return ONLY valid JSON.
- Do not use markdown.
- Do not use code fences.

Quiz results:
----------------
{result_text}
----------------

Return exactly this JSON structure:

{{
    "weak_topics": [
        "Topic 1",
        "Topic 2"
    ],
    "revision_advice": [
        "Advice 1",
        "Advice 2"
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
            ],
            options={
                "temperature": 0.1,
                "num_predict": 500
            }
        )

        content = response["message"]["content"].strip()

        # Remove accidental markdown fences
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

        analysis = json.loads(content)

        # Make sure the expected structure exists
        if not isinstance(analysis, dict):
            raise ValueError("Invalid analysis format returned by Gemma.")

        if "weak_topics" not in analysis:
            analysis["weak_topics"] = []

        if "revision_advice" not in analysis:
            analysis["revision_advice"] = []

        return {
            "success": True,
            "analysis": analysis
        }

    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Gemma returned invalid JSON for weak-topic analysis."
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Weak-topic analysis failed: {str(e)}"
        }

# ============================================================
# DOCUMENT STATUS
# ============================================================

@app.get("/api/documents")
def get_documents():
    documents = get_indexed_documents()

    return {
        "success": True,
        "documents": documents
    }


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )