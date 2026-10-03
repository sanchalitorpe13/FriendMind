# 🧠 FriendMind

> **A private, document-grounded AI study companion that helps you learn from your own study material, test your knowledge, and discover what to revise next.**

Built for the **Hacktoberfest 2026 DEV Weekend Challenge — “Build for a Friend.”**

![FriendMind home](docs/home.png)

## 💡 What is FriendMind?

FriendMind turns your study PDFs into an interactive learning assistant.

```text
📄 Upload Notes
      ↓
🧠 Index & Embed
      ↓
🔎 Semantic Search
      ↓
💬 Ask Questions
      ↓
📝 Generate Quiz
      ↓
✅ Evaluate Answers
      ↓
📊 Find Weak Topics
```

Unlike a generic chatbot, FriendMind grounds its answers and quizzes in the user's uploaded study material.

---

## ✨ Features

- 📄 **PDF Upload & Processing**
- 🧠 **Semantic Embeddings** with Sentence Transformers
- 🔎 **Semantic Search** using ChromaDB
- 📚 **RAG-based Question Answering**
- 🤖 **Local LLM** using Ollama + Gemma 3
- 🛡️ **Context Protection** against unsupported answers
- 📝 **AI Quiz Generation**
- 🎚️ **5/10 Questions + Easy/Medium/Hard**
- 🧠 **Semantic Answer Verification**
- 📊 **Weak Topic Detection**
- 💾 **Persistent Document Storage**
- ♻️ **Duplicate Upload Protection**
- 🌙 **Responsive Light/Dark UI**
- 🔒 **Local-first Architecture**

---

## 📸 Demo

| 1. Upload your notes | 2. Ask a question |
|---|---|
| ![Upload](docs/upload.png) | ![Ask](docs/ask.png) |

| 3. Take a quiz | 4. Find weak topics |
|---|---|
| ![Quiz](docs/quiz.png) | ![Results](docs/results.png) |

---

## 🧠 Semantic Quiz Verification

FriendMind does not rely only on exact string matching.

For example:

```text
Expected:
Binary search has logarithmic time complexity.

User:
Binary search runs in O(log n).
```

Different wording, same concept.

FriendMind uses semantic similarity to evaluate natural-language answers more flexibly.

---

## 🏗️ Architecture

```text
                 ┌───────────────┐
                 │   index.html  │
                 │   Web UI      │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │    FastAPI    │
                 │    app.py     │
                 └───────┬───────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     PDF Processing   RAG Engine    Quiz Engine
                      src/rag.py    src/quiz.py
          │              │              │
          │              ▼              │
          │         Sentence           │
          │         Transformers      │
          │              │              │
          │              ▼              │
          │          ChromaDB           │
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                    Ollama
                   Gemma 3
```

---

## 🛠️ Tech Stack

**Backend:** Python, FastAPI, Uvicorn  
**AI/ML:** Sentence Transformers, RAG, Semantic Similarity  
**LLM:** Ollama, Gemma 3  
**Vector Database:** ChromaDB  
**Document Processing:** pypdf  
**Frontend:** HTML, CSS, Vanilla JavaScript  
**Development:** Git, GitHub, PowerShell, VS Code

---

## 📁 Project Structure

```text
FriendMind/
├── app.py
├── index.html
├── requirements.txt
├── README.md
├── .gitignore
├── docs/          # README screenshots
└── src/
    ├── rag.py
    └── quiz.py
```

---

## ⚙️ Setup

### 1. Clone

```bash
git clone https://github.com/sanchalitorpe13/FriendMind.git
cd FriendMind
```

### 2. Create virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Install and run Ollama

Pull the required model:

```powershell
ollama pull gemma3:4b
```

Make sure Ollama is running.

### 5. Start FriendMind

```powershell
python app.py
```

Open:

**http://127.0.0.1:8000**

> Open the application through FastAPI rather than directly opening `index.html`. Using VS Code Live Server (port 5500) causes "Failed to fetch".

---

## 🧪 Example Workflow

1. Upload a study PDF.
2. Ask a question about the material.
3. Generate a 5 or 10-question quiz.
4. Submit your answers.
5. Review semantic evaluation and explanations.
6. Check detected weak topics.
7. Revise and try again.

---

## 🔌 API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/documents` | Indexed documents |
| POST | `/api/upload` | Upload PDF |
| POST | `/api/ask` | Ask grounded question |
| POST | `/api/quiz` | Generate quiz |
| POST | `/api/weak-topics` | Analyze weak topics |

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 🔒 Privacy

FriendMind follows a **local-first approach**:

```text
Your PDF
   ↓
Your Computer
   ↓
ChromaDB
   ↓
Local Embeddings
   ↓
Ollama / Gemma 3
```

The core AI workflow can run locally without sending study material to a cloud LLM provider.

---

## 🎯 Why FriendMind?

FriendMind is designed around one simple idea:

> **AI should not only give you answers — it should help you learn.**

It combines:

**RAG + Local LLM + Semantic Search + Quiz Generation + Semantic Evaluation + Weak Topic Detection**

into one focused learning workflow.

---

## 🚀 Future Improvements

- Topic-wise quizzes
- More document formats
- Improved citations
- Learning analytics
- Personalized revision plans
- Conversation history
- Hybrid retrieval
- Streaming responses

---

## 🧑‍💻 Author

**Sanchali Torpe**  
B.Tech Computer Engineering  
Sanjivani College of Engineering

**Interests:** AI/ML • Generative AI • Agentic AI • Open Source • Software Development

---

## ❤️ Built for a Friend

**Built for a friend. Built for learning. Built with AI.**
