import streamlit as st
import ollama
from pypdf import PdfReader

from src.rag import add_document, search_documents


# -----------------------------------
# Page configuration
# -----------------------------------

st.set_page_config(
    page_title="FriendMind",
    page_icon="🧠",
    layout="centered",
)


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
# Footer
# -----------------------------------

st.divider()

st.caption(
    "Powered by Gemma 3 4B • Ollama • ChromaDB • Streamlit"
)