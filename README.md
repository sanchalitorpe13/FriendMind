# 🧠 FriendMind

> **A private, document-grounded AI study companion that helps you understand your own study material, test your knowledge, and identify weak topics.**

FriendMind is an AI-powered study assistant built for the **Hacktoberfest 2026 DEV Weekend Challenge — "Build for a Friend."**

The idea is simple:

**Give FriendMind your study material → ask questions → generate a quiz → check your understanding → discover weak topics.**

Instead of giving generic AI answers, FriendMind uses your uploaded documents as the knowledge source and grounds its responses in the material you provide.

---

## ✨ Why FriendMind?

Studying from long PDFs and notes can be difficult.

You may:

- Spend too much time searching through notes.
- Forget where a particular concept was explained.
- Ask an AI a question and receive information that isn't in your syllabus.
- Practice questions without knowing which topics you are weak in.
- Re-upload the same study material multiple times.
- Lose your indexed study material when restarting the application.

FriendMind was designed around these problems.

It provides a focused workflow:

```text
📄 Upload Study Material
        ↓
🧠 Process & Index
        ↓
🔎 Retrieve Relevant Content
        ↓
💬 Ask Questions
        ↓
📝 Generate Quiz
        ↓
✅ Verify Answers
        ↓
📊 Identify Weak Topics
```

---

# 🚀 Features

| Feature | Description |
|---|---|
| 📄 PDF Upload | Drag and drop your own study material |
| ✂️ Text Chunking | Splits documents into smaller searchable sections |
| 🧠 Semantic Embeddings | Converts document chunks into vector representations |
| 🔎 Semantic Search | Retrieves content relevant to a question |
| 🤖 Local LLM | Uses Ollama with Gemma 3 for answer generation |
| 📚 RAG | Grounds answers using retrieved study material |
| 🔍 Source Display | Shows the exact chunks used to produce each answer |
| 🛡️ Context Protection | Refuses to answer when information isn't supported by the uploaded material |
| 📝 Quiz Generation | Creates quizzes from indexed study material |
| 🎚️ Quiz Options | Choose 5 or 10 questions and Easy, Medium or Hard difficulty |
| 🧠 Semantic Verification | Evaluates answers based on meaning rather than exact wording |
| 🧾 Answer Review | Shows your answer, the correct answer and an explanation for every question |
| 📊 Weak Topic Detection | Identifies topics where the learner needs more practice |
| 💾 Persistent Storage | Keeps indexed documents available between restarts |
| ♻️ Duplicate Protection | Prevents duplicate chunks when the same document is uploaded again |
| 🎨 Modern Web UI | Responsive interface with live stats, loading states and automatic dark mode |
| 🔒 Local-first Architecture | Designed to keep study material and inference on the local machine |

---

# 🖥️ The Interface

FriendMind ships with a single-page web interface (`index.html`) served by the FastAPI backend.

| Section | What it does |
|---|---|
| **Hero + Upload** | Drag and drop a PDF. Shows file name, page count and chunks indexed once it is ready. |
| **Live stats** | Study material status, indexed chunks, latest quiz score and the AI engine in use. |
| **Ask FriendMind** | Ask a question about your notes. The answer is shown with the source chunks it came from. |
| **Quiz** | Choose the number of questions and difficulty, answer in the browser, then submit. |
| **Results** | Score card, per-question review with explanations, and an AI analysis of weak topics. |
| **How it works** | A short three-step explanation of the learning loop. |

The interface follows the system light or dark setting, works on phones and tablets, and uses no frontend framework or build step.

---

# 🧩 How FriendMind Works

## 1. Upload your study material

The user uploads a PDF containing notes, textbooks, lecture material, or other study resources.

FriendMind extracts the text from the document.

```text
PDF
 ↓
Text Extraction
 ↓
Clean Text
```

---

## 2. Split the document into chunks

Large documents are divided into smaller pieces.

This makes semantic retrieval more precise and prevents the entire document from being sent to the language model for every question.

```text
Document
   ↓
Chunk 1
Chunk 2
Chunk 3
...
Chunk N
```

---

## 3. Generate embeddings

Each chunk is converted into a numerical vector using a Sentence Transformer embedding model.

Conceptually:

```text
"Binary search has O(log n) complexity"
                    ↓
            Embedding Vector
```

These vectors allow FriendMind to search for **semantic similarity** rather than relying only on exact keyword matching.

---

## 4. Store the embeddings

FriendMind stores the document chunks and their embeddings in **ChromaDB**.

The database is persistent, meaning the indexed documents can remain available even after the application is restarted.

---

## 5. Ask a question

When the user asks a question:

```text
User Question
      ↓
Question Embedding
      ↓
Semantic Search
      ↓
Relevant Document Chunks
```

FriendMind retrieves the most relevant parts of the uploaded study material.

---

## 6. Generate a grounded answer

The retrieved context is passed to the local language model.

FriendMind uses:

**Ollama + Gemma 3**

The model generates an answer based on the retrieved material.

The goal is not simply to ask an LLM:

```text
"Answer this question."
```

Instead, FriendMind follows a grounded approach:

```text
Question
   +
Retrieved Study Material
   ↓
Local LLM
   ↓
Grounded Answer
```

---

# 🛡️ Out-of-Context Protection

One important design goal of FriendMind is reducing unsupported answers.

If the uploaded study material does not contain enough information to answer a question, FriendMind can refuse instead of confidently generating unrelated information.

For example:

```text
Uploaded material:
Data Structures notes

Question:
"What is the capital of France?"
```

Instead of inventing an answer from general model knowledge, FriendMind can respond that the information is not available in the provided study material.

This keeps the assistant focused on the learner's actual material.

---

# 📝 Quiz Generation

FriendMind can generate quizzes from the indexed study material.

The learner chooses:

- **Number of questions:** 5 or 10
- **Difficulty:** Easy, Medium or Hard

The quiz workflow is:

```text
Study Material
      ↓
Relevant Content
      ↓
Question Generation
      ↓
Quiz
      ↓
User Answers
```

Each question includes answer options, the correct answer and a short explanation that is shown during review.

This allows the learner to move from passive reading to active recall.

---

# 🧠 Semantic Quiz Verification

Traditional quiz systems often compare answers using exact string matching.

For example:

```text
Expected:
"Machine learning"

User:
"machine learning"
```

Exact comparison works here.

But consider:

```text
Expected:
"Binary search has logarithmic time complexity."

User:
"The running time of binary search is O(log n)."
```

The wording is different, but the meaning is essentially the same.

FriendMind therefore includes a **semantic verification layer**.

Instead of relying only on exact text matching, the system evaluates whether the user's answer is semantically consistent with the expected answer.

Conceptually:

```text
Expected Answer
       ↓
   Embedding
       ↘
        Semantic Similarity
       ↗
User Answer
       ↓
Correct / Incorrect
```

This makes quiz evaluation more flexible and useful for natural-language answers.

---

# 📊 Weak Topic Detection

After completing a quiz, FriendMind analyzes incorrect answers and identifies topics that may require additional revision.

Example:

```text
Quiz Results

Arrays          ✅
Linked Lists    ❌
Stacks          ✅
Queues          ❌
Trees           ❌
```

FriendMind can identify:

```text
Weak Topics:
- Linked Lists
- Queues
- Trees
```

The analysis is returned in three parts:

```text
⚠️ Weak Topics
📚 What to Revise
🎯 Practice Recommendation
```

The purpose is to turn quiz results into an actionable study direction.

Instead of simply saying:

> "You scored 6/10."

FriendMind can help answer:

> "What should I revise next?"

If every answer is correct, FriendMind suggests trying a harder quiz instead.

---

# 💾 Persistent Documents

FriendMind uses persistent ChromaDB storage.

This means indexed documents are not limited to the current Python process.

After restarting the application, previously indexed documents can still be available.

The API also exposes document information so the current indexed material can be inspected.

Example:

```text
GET /api/documents
```

---

# ♻️ Duplicate Upload Protection

FriendMind also handles repeated uploads of the same document.

When a document is indexed, its chunks are associated with the document name.

If the same document is uploaded again, previously indexed chunks for that document are removed before the new chunks are added.

This prevents a situation such as:

```text
Upload notes.pdf
        ↓
19 chunks

Upload notes.pdf again
        ↓
38 chunks ❌
```

Instead:

```text
Upload notes.pdf
        ↓
19 chunks

Upload notes.pdf again
        ↓
19 chunks ✅
```

---

# 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │      User / UI       │
                    │      index.html      │
                    └──────────┬───────────┘
                               │  fetch /api/...
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI         │
                    │       app.py         │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
      ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
      │ PDF Text    │   │ RAG Engine  │   │ Quiz Engine │
      │ Extraction  │   │  src/rag.py │   │ src/quiz.py │
      └─────────────┘   └──────┬──────┘   └─────────────┘
                               │
                     ┌─────────┴─────────┐
                     │                   │
                     ▼                   ▼
              ┌──────────────┐   ┌──────────────┐
              │ Sentence     │   │  ChromaDB    │
              │ Transformers │   │ Vector Store │
              └──────────────┘   └──────────────┘
                               │
                               ▼
                       ┌──────────────┐
                       │   Ollama     │
                       │   Gemma 3    │
                       └──────────────┘
```

The frontend and backend are served from the same address, so there is no separate frontend server and no CORS configuration to manage.

---

# 🔄 RAG Pipeline

FriendMind's retrieval-augmented generation pipeline can be summarized as:

```text
                DOCUMENT INGESTION

PDF
 │
 ▼
Text Extraction
 │
 ▼
Chunking
 │
 ▼
Embedding Model
 │
 ▼
ChromaDB
 │
 ▼
Persistent Knowledge Base


                 QUESTION ANSWERING

User Question
 │
 ▼
Question Embedding
 │
 ▼
Semantic Retrieval
 │
 ▼
Relevant Chunks
 │
 ▼
Prompt + Context
 │
 ▼
Gemma 3 via Ollama
 │
 ▼
Grounded Answer
```

---

# 🔌 API Reference

The web interface talks to these endpoints. They can also be called directly.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Serves the web interface (`index.html`) |
| `GET` | `/api/health` | Health check: status, model and document count |
| `GET` | `/api/documents` | Lists the documents currently indexed |
| `POST` | `/api/upload` | Uploads a PDF (multipart form field `file`). Returns file name, page count and chunk count |
| `POST` | `/api/ask` | Body: `{"question": "..."}`. Returns a grounded `answer` and the `sources` used |
| `POST` | `/api/quiz` | Body: `{"num_questions": 5, "difficulty": "Medium"}`. Returns the generated questions |
| `POST` | `/api/weak-topics` | Body: `{"incorrect": [...]}`. Returns an `analysis` of weak topics |

FastAPI also generates interactive documentation at `http://127.0.0.1:8000/docs`.

---

# 🛠️ Tech Stack

## Backend

- Python
- FastAPI
- Uvicorn

## AI / ML

- Sentence Transformers
- Embeddings
- Semantic similarity
- Retrieval-Augmented Generation (RAG)
- Ollama
- Gemma 3

## Vector Database

- ChromaDB

## Document Processing

- PDF text extraction (pypdf)
- Text chunking

## Frontend

- HTML
- CSS (custom properties, automatic dark mode)
- Vanilla JavaScript (no framework, no build step)

## Development

- Git
- GitHub
- PowerShell
- VS Code

---

# 📁 Project Structure

```text
FriendMind/
│
├── .gitignore
├── app.py
├── index.html
├── README.md
├── requirements.txt
│
└── src/
    ├── quiz.py
    └── rag.py
```

### File Responsibilities

### `app.py`

Main FastAPI application.

Handles the application's API endpoints, serves the web interface, and connects the frontend with the RAG and quiz functionality.

---

### `src/rag.py`

Responsible for the retrieval pipeline.

Main responsibilities include:

- Document processing
- Text chunking
- Embedding generation
- ChromaDB storage
- Semantic retrieval
- Document persistence
- Duplicate-upload handling

---

### `src/quiz.py`

Responsible for quiz-related functionality.

Includes:

- Quiz generation
- Answer evaluation
- Semantic verification
- Weak-topic analysis

---

### `index.html`

Single-file frontend. Contains the page structure, styling and the JavaScript that calls the API for uploads, questions, quizzes and results.

---

### `requirements.txt`

Contains the Python dependencies required to run the project.

---

### `.gitignore`

Prevents generated and environment-specific files from being committed.

Examples include:

```text
venv/
__pycache__/
*.pyc
.env
chroma_db/
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd FriendMind
```

---

## 2. Create a virtual environment

### Windows

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

Make sure `requirements.txt` includes at least:

```text
fastapi
uvicorn
python-multipart
pypdf
ollama
chromadb
sentence-transformers
```

`python-multipart` is required for PDF uploads.

---

# 🤖 Install Ollama

FriendMind uses Ollama for local LLM inference.

Install Ollama for your operating system and make sure it is running.

Then pull the Gemma 3 model:

```powershell
ollama pull gemma3:4b
```

Verify that the model is available:

```powershell
ollama list
```

You should see the Gemma model in the list.

---

# ▶️ Run FriendMind

Start the FastAPI application:

```powershell
python app.py
```

Or, with auto-reload while developing:

```powershell
uvicorn app:app --reload
```

The application should start on:

```text
http://127.0.0.1:8000
```

Open that address in your browser.

> **Important:** open FriendMind through the FastAPI address above. Opening `index.html` by double-clicking it, or through an editor extension such as VS Code Live Server (port 5500), loads the page but the buttons cannot reach the API.

---

# 🩺 Health Check

FriendMind exposes a health endpoint.

Run:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

A healthy installation should return information similar to:

```text
status      : healthy
model       : gemma3:4b
documents   : 2
```

The document count depends on how many documents have been indexed.

---

# 📚 Check Indexed Documents

You can inspect the documents currently stored in the vector database:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/documents
```

This can be useful for verifying persistence and duplicate-upload behavior.

---

# 🧪 Example Workflow

Once FriendMind is running:

### Step 1 — Upload

Drag a PDF containing your study material onto the upload area.

```text
📄 Data Structures Notes.pdf
```

The page confirms the file name, page count and number of chunks indexed.

---

### Step 2 — Ask

Open **Ask FriendMind** and ask a question related to the document.

Example:

```text
What is the time complexity of binary search?
```

FriendMind retrieves the relevant section, generates a grounded response, and lists the source chunks it used.

---

### Step 3 — Test Yourself

Open the **Quiz** tab, choose the number of questions and difficulty, and generate a quiz from the study material.

Example:

```text
Question 1:
What is the main advantage of a binary search tree?
```

---

### Step 4 — Submit Answers

Select your answers and submit the quiz.

FriendMind scores your answers and shows a review with the correct answer and an explanation for each question.

---

### Step 5 — Analyze Weak Topics

After the quiz, FriendMind identifies topics associated with incorrect answers.

```text
Weak Topics
────────────
Trees
Binary Search
Recursion
```

You can then return to the relevant material and revise those areas, or take another quiz.

---

# 🔧 Troubleshooting

| Problem | Likely cause and fix |
|---|---|
| **"Failed to fetch"** when uploading or asking | The page is not being served by FastAPI. Start the app with `python app.py` and open `http://127.0.0.1:8000`, not a Live Server or `file://` address. |
| **Upload returns an error about form data** | `python-multipart` is missing. Run `pip install python-multipart`. |
| **"No readable text found"** | The PDF is probably scanned images. Use a PDF with selectable text, or run OCR on it first. |
| **Questions or quizzes fail or time out** | Ollama is not running, or the model is missing. Start Ollama and run `ollama pull gemma3:4b`. The first response can be slow while the model loads. |
| **"No study material found"** | Nothing is indexed yet. Upload a PDF first, then ask or generate a quiz. |
| **`ModuleNotFoundError: src`** | Run the app from the project root, the folder that contains `app.py` and `src/`. |
| **Port 8000 already in use** | Stop the other process, or start on another port with `uvicorn app:app --port 8001`. |

---

# 🔒 Privacy

FriendMind is designed with a **local-first approach**.

The core AI workflow can run on the user's own machine:

```text
Your PDF
   ↓
Your Computer
   ↓
ChromaDB
   ↓
Local Embeddings
   ↓
Local Ollama / Gemma
```

This is particularly useful for personal notes, academic material, and documents that users may not want to upload to a third-party AI service.

The web interface loads its font from Google Fonts. Everything else, including your documents and questions, stays on your machine.

> **Note:** Actual privacy depends on the configuration of the user's environment and any external services they choose to use.

---

# 🎯 Hacktoberfest 2026

FriendMind was built for the **DEV Weekend Challenge — "Build for a Friend"** as part of Hacktoberfest 2026.

The project focuses on building something useful for a real study problem rather than creating another generic chatbot.

The central idea is:

> **Build an AI study companion that works with the learner's own material.**

FriendMind combines:

```text
RAG
+
Local LLM
+
Semantic Search
+
Quiz Generation
+
Semantic Evaluation
+
Weak Topic Detection
```

into a single study workflow.

---

# 💡 Design Philosophy

FriendMind follows several principles.

## 1. Ground answers in the user's material

The assistant should prioritize the learner's uploaded study material rather than freely generating unrelated information.

---

## 2. Reduce unsupported answers

If the required information is not available in the indexed material, the system should avoid pretending that it is.

---

## 3. Turn AI into an active-learning tool

FriendMind isn't only designed for:

```text
Question → Answer
```

It also supports:

```text
Study
 ↓
Practice
 ↓
Evaluate
 ↓
Identify Weaknesses
 ↓
Revise
```

---

## 4. Keep the architecture understandable

The project uses a relatively straightforward architecture so that the individual components can be understood and improved independently. The frontend is one HTML file with no build step, and the backend is a small FastAPI app.

---

# 📈 Future Improvements

- [x] Difficulty levels for quizzes
- [x] Improved citation display for retrieved chunks
- [x] Better frontend UX
- [ ] Support for more document formats
- [ ] Better document organization
- [ ] Topic-wise quiz generation
- [ ] More detailed learning analytics
- [ ] Study progress tracking across sessions
- [ ] Personalized revision plans
- [ ] Conversation history
- [ ] Multiple subject workspaces
- [ ] Streaming LLM responses
- [ ] More advanced retrieval strategies
- [ ] Hybrid keyword + semantic retrieval
- [ ] Improved semantic answer evaluation

---

# ⚠️ Limitations

FriendMind is an experimental educational project.

Some limitations include:

- Answer quality depends on the quality of the uploaded material.
- PDF extraction may not work perfectly with scanned/image-only PDFs.
- Semantic evaluation can occasionally misinterpret answers.
- Local LLM performance depends on the available hardware.
- Retrieval quality depends on chunking and embedding quality.
- Quiz scores are shown for the current session only and are not saved.
- The application is currently designed primarily for local, single-user use.

---

# 🤝 Contributing

Contributions are welcome!

A simple workflow:

```bash
# Fork the repository

# Clone your fork
git clone <YOUR_FORK_URL>

# Create a branch
git checkout -b feature/your-feature

# Make your changes

# Test the application

# Commit
git add .
git commit -m "Add your feature"

# Push
git push origin feature/your-feature

# Open a Pull Request
```

Before submitting a pull request, please make sure that:

- The application still starts successfully.
- Existing functionality is not unnecessarily broken.
- New dependencies are documented in `requirements.txt`.
- Generated files and local environments are not committed.
- The change is focused and understandable.

---

# 🧑‍💻 Author

**Sanchali Torpe**

B.Tech Computer Engineering  
Sanjivani College of Engineering

Interested in:

- Artificial Intelligence
- Machine Learning
- Generative AI
- Agentic AI
- Open Source
- Software Development

---

# ❤️ Built for a Friend

FriendMind started with a simple idea:

**AI should not only give you answers — it should help you learn.**

Instead of replacing the learning process, FriendMind is designed to support it:

```text
📚 Learn
   ↓
🤔 Ask
   ↓
📝 Practice
   ↓
✅ Evaluate
   ↓
📊 Understand Weaknesses
   ↓
🚀 Improve
```

**Built for a friend. Built for learning. Built with AI.**

---

## 📜 License

This project is intended as an open-source project for learning, experimentation, and collaboration.

See the repository for the applicable license information.
