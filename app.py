import streamlit as st
import ollama
from pypdf import PdfReader

from src.rag import add_document, search_documents
from src.quiz import generate_quiz


# -----------------------------------
# Page configuration
# -----------------------------------

st.set_page_config(
    page_title="FriendMind",
    page_icon="🧠",
    layout="centered",
)


# -----------------------------------
# Weak Topic Detection
# -----------------------------------

def detect_weak_topics(incorrect_questions):

    if not incorrect_questions:
        return "🎉 Great job! You did not get any questions wrong."

    question_text = "\n\n".join(
        [
            f"Question: {item['question']}\n"
            f"Correct Answer: {item['correct_answer']}\n"
            f"Student Answer: {item['student_answer']}"
            for item in incorrect_questions
        ]
    )

    prompt = f"""
You are FriendMind, a personal AI study companion.

Analyze the questions the student answered incorrectly.

Identify the concepts or topics that appear to be weak based ONLY
on the questions and answers provided below.

Incorrect questions:
----------------
{question_text}
----------------

Give a concise response in this format:

### ⚠️ Weak Topics

- Topic 1 — brief reason
- Topic 2 — brief reason

### 📚 What to Revise

Give 2-4 specific concepts the student should revise.

### 🎯 Practice Recommendation

Give one short recommendation for what the student should practice next.

Do not invent topics that cannot reasonably be identified from
the questions provided.
"""

    response = ollama.chat(
        model="gemma3:4b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response["message"]["content"]


# -----------------------------------
# Gemma
# -----------------------------------

def ask_gemma(question, context):

    prompt = f"""
You are FriendMind, a personal AI study companion.

Answer the student's question using the study material provided below.

IMPORTANT RULES:
1. Prefer information from the provided study material.
2. Explain concepts clearly and simply.
3. If the study material does not contain enough information,
   say that the uploaded material does not provide enough information.
4. Do not pretend that information came from the notes if it did not.

STUDY MATERIAL:
----------------
{context}
----------------

STUDENT QUESTION:
{question}

Give a helpful, student-friendly answer.
"""

    response = ollama.chat(
        model="gemma3:4b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response["message"]["content"]


# -----------------------------------
# Header
# -----------------------------------

st.title("🧠 FriendMind")

st.subheader(
    "Your Personal AI Study Companion"
)

st.write(
    "Upload your study material and ask questions. "
    "FriendMind retrieves relevant information from your notes "
    "and uses Gemma to explain it."
)

st.divider()


# -----------------------------------
# Upload study material
# -----------------------------------

st.markdown("### 📚 Upload Study Material")

uploaded_file = st.file_uploader(
    "Upload your study notes or textbook PDF",
    type=["pdf"],
)


# -----------------------------------
# Process PDF
# -----------------------------------

if uploaded_file is not None:

    try:

        reader = PdfReader(uploaded_file)

        page_count = len(reader.pages)

        extracted_text = ""

        for page in reader.pages:

            text = page.extract_text()

            if text:
                extracted_text += text + "\n"

        if extracted_text.strip():

            st.success(
                f"✅ PDF uploaded successfully — "
                f"{page_count} page(s)"
            )

            st.info(
                f"Extracted approximately "
                f"{len(extracted_text):,} characters."
            )

            # -----------------------------------
            # Add document to ChromaDB
            # -----------------------------------

            if (
                "processed_file" not in st.session_state
                or st.session_state["processed_file"]
                != uploaded_file.name
            ):

                with st.spinner(
                    "Processing your study material..."
                ):

                    chunk_count = add_document(
                        extracted_text,
                        uploaded_file.name,
                    )

                st.session_state["processed_file"] = (
                    uploaded_file.name
                )

                st.session_state["chunk_count"] = (
                    chunk_count
                )

            if "chunk_count" in st.session_state:

                st.success(
                    f"🧠 Study material ready! "
                    f"{st.session_state['chunk_count']} "
                    f"chunk(s) indexed."
                )

            # -----------------------------------
            # Preview
            # -----------------------------------

            with st.expander(
                "📄 Preview extracted text"
            ):

                st.text_area(
                    "Extracted text",
                    extracted_text[:3000],
                    height=250,
                    label_visibility="collapsed",
                )

        else:

            st.warning(
                "No readable text was found in this PDF. "
                "It may contain scanned images."
            )

    except Exception as e:

        st.error(
            "Could not process this PDF."
        )

        st.code(str(e))


st.divider()


# -----------------------------------
# Ask FriendMind
# -----------------------------------

st.markdown("### 💬 Ask FriendMind")

question = st.text_area(
    "What would you like to learn?",
    placeholder=(
        "Example: Explain the concept of a full adder "
        "from my notes."
    ),
    height=120,
)


# -----------------------------------
# Ask button
# -----------------------------------

if st.button(
    "🤖 Ask FriendMind",
    use_container_width=True,
):

    if not question.strip():

        st.warning(
            "Please enter a question first."
        )

    elif "processed_file" not in st.session_state:

        st.warning(
            "Please upload your study material first."
        )

    else:

        with st.spinner(
            "Searching your study material..."
        ):

            try:

                results = search_documents(
                    question,
                    top_k=3,
                )

                documents = results.get(
                    "documents",
                    [[]],
                )[0]

                if not documents:

                    st.warning(
                        "I couldn't find relevant information "
                        "in your uploaded material."
                    )

                else:

                    context = "\n\n".join(
                        documents
                    )

                    with st.spinner(
                        "FriendMind is thinking..."
                    ):

                        answer = ask_gemma(
                            question,
                            context,
                        )

                    st.markdown(
                        "### 📚 FriendMind's Answer"
                    )

                    st.markdown(answer)

                    # -----------------------------------
                    # Retrieved sources
                    # -----------------------------------

                    with st.expander(
                        "🔎 Sources retrieved from your notes"
                    ):

                        for index, document in enumerate(
                            documents,
                            start=1,
                        ):

                            st.markdown(
                                f"**Source chunk {index}**"
                            )

                            st.write(document)

            except Exception as e:

                st.error(
                    "Something went wrong while "
                    "searching the study material."
                )

                st.code(str(e))


# -----------------------------------
# Quiz Generator
# -----------------------------------

st.divider()

st.header("📝 Quiz Generator")

st.write(
    "Test your understanding using questions generated "
    "from your uploaded study material."
)


# -----------------------------------
# Quiz session state
# -----------------------------------

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = None

if "quiz_percentage" not in st.session_state:
    st.session_state.quiz_percentage = None

if "incorrect_questions" not in st.session_state:
    st.session_state.incorrect_questions = []


# -----------------------------------
# Quiz settings
# -----------------------------------

if st.session_state.get("processed_file"):

    col1, col2 = st.columns(2)

    with col1:

        num_questions = st.selectbox(
            "Number of questions",
            [5, 10],
            index=0,
        )

    with col2:

        difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard"],
            index=1,
        )

    # -----------------------------------
    # Generate Quiz
    # -----------------------------------

    if st.button(
        "🧠 Generate Quiz",
        use_container_width=True,
    ):

        with st.spinner(
            "FriendMind is creating your quiz..."
        ):

            try:

                # Retrieve fewer chunks for faster generation
                results = search_documents(
                    "important concepts definitions key topics",
                    top_k=3,
                )

                documents = results.get(
                    "documents",
                    [[]],
                )[0]

                if not documents:

                    st.error(
                        "No relevant study material was found "
                        "for quiz generation."
                    )

                else:

                    context = "\n\n".join(
                        documents
                    )

                    quiz = generate_quiz(
                        context=context,
                        num_questions=num_questions,
                        difficulty=difficulty,
                    )

                    st.session_state.quiz = quiz
                    st.session_state.quiz_answers = {}

                    # Clear previous results
                    st.session_state.quiz_score = None
                    st.session_state.quiz_percentage = None
                    st.session_state.incorrect_questions = []

            except Exception as e:

                st.error(
                    "Could not generate the quiz."
                )

                st.code(str(e))

else:

    st.info(
        "📚 Upload and process a study PDF first."
    )


# -----------------------------------
# Display Quiz
# -----------------------------------

if st.session_state.quiz:

    quiz = st.session_state.quiz

    if "error" in quiz:

        st.error(
            quiz["error"]
        )

        # Show raw response only when debugging is needed
        if "raw_response" in quiz:

            with st.expander(
                "🔎 View Gemma response"
            ):

                st.code(
                    quiz["raw_response"]
                )

    else:

        questions = quiz.get(
            "questions",
            []
        )

        if questions:

            st.subheader("📖 Your Quiz")

            # -----------------------------------
            # Display questions
            # -----------------------------------

            for i, quiz_question in enumerate(
                questions
            ):

                st.markdown(
                    f"### Question {i + 1}"
                )

                st.write(
                    quiz_question["question"]
                )

                answer = st.radio(
                    "Choose your answer:",
                    quiz_question["options"],
                    key=f"quiz_question_{i}",
                )

                st.session_state.quiz_answers[i] = answer

                st.divider()

            # -----------------------------------
            # Submit Quiz
            # -----------------------------------

            if st.button(
                "✅ Submit Quiz",
                use_container_width=True,
            ):

                score = 0

                incorrect_questions = []

                # -----------------------------------
                # Calculate score
                # -----------------------------------

                for i, quiz_question in enumerate(
                    questions
                ):

                    selected_answer = (
                        st.session_state.quiz_answers.get(i)
                    )

                    # IMPORTANT:
                    # answer is now the actual answer text,
                    # not an integer index.
                    correct_answer = quiz_question["answer"]

                    if selected_answer == correct_answer:

                        score += 1

                    else:

                        incorrect_questions.append(
                            {
                                "question": quiz_question["question"],
                                "correct_answer": correct_answer,
                                "student_answer": (
                                    selected_answer
                                    if selected_answer
                                    else "No answer selected"
                                ),
                            }
                        )

                # -----------------------------------
                # Calculate percentage
                # -----------------------------------

                percentage = (
                    int(
                        (score / len(questions)) * 100
                    )
                    if questions
                    else 0
                )

                # -----------------------------------
                # Save result
                # -----------------------------------

                st.session_state.quiz_score = score

                st.session_state.quiz_percentage = (
                    percentage
                )

                st.session_state.incorrect_questions = (
                    incorrect_questions
                )

                # -----------------------------------
                # Show Score
                # -----------------------------------

                st.success(
                    f"🎉 You scored {score}/{len(questions)} "
                    f"({percentage}%)"
                )

                # -----------------------------------
                # Answer Review
                # -----------------------------------

                st.subheader(
                    "📚 Answer Review"
                )

                for i, quiz_question in enumerate(
                    questions
                ):

                    selected_answer = (
                        st.session_state.quiz_answers.get(i)
                    )

                    # IMPORTANT:
                    # answer is actual text
                    correct_answer = quiz_question["answer"]

                    if selected_answer == correct_answer:

                        st.success(
                            f"Question {i + 1}: Correct ✅"
                        )

                    else:

                        st.error(
                            f"Question {i + 1}: Incorrect ❌"
                        )

                        st.write(
                            f"Your answer: "
                            f"**{selected_answer if selected_answer else 'No answer selected'}**"
                        )

                        st.write(
                            f"Correct answer: "
                            f"**{correct_answer}**"
                        )

                    st.caption(
                        f"Explanation: "
                        f"{quiz_question.get('explanation', 'No explanation available.')}"
                    )

                # -----------------------------------
                # Weak Topic Detection
                # -----------------------------------

                st.divider()

                st.subheader(
                    "🎯 FriendMind's Learning Analysis"
                )

                if incorrect_questions:

                    with st.spinner(
                        "🧠 FriendMind is analyzing "
                        "your mistakes..."
                    ):

                        weak_topics = detect_weak_topics(
                            incorrect_questions
                        )

                    st.markdown(
                        weak_topics
                    )

                else:

                    st.success(
                        "🌟 Excellent! You answered "
                        "every question correctly."
                    )

                    st.info(
                        "You can try a harder quiz "
                        "to challenge yourself."
                    )

        else:

            st.warning(
                "No quiz questions were generated."
            )


# -----------------------------------
# Footer
# -----------------------------------

st.divider()

st.caption(
    "Powered by Gemma 3 4B • Ollama • ChromaDB • Streamlit"
)