import chromadb
from sentence_transformers import SentenceTransformer


# -----------------------------
# Embedding model
# -----------------------------
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# -----------------------------
# ChromaDB
# -----------------------------
chroma_client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="friendmind_documents"
)


# -----------------------------
# Text chunking
# -----------------------------
def split_text(text, chunk_size=1000, overlap=200):
    """
    Split extracted document text into overlapping chunks.
    """

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# -----------------------------
# Add document to vector DB
# -----------------------------

def add_document(text, document_name="study_material"):
    chunks = split_text(text)

    if not chunks:
        return 0

    # Remove previously indexed chunks for the same document.
    existing = collection.get(
        where={"source": document_name},
        include=["metadatas"]
    )

    existing_ids = existing.get("ids", []) or []

    if existing_ids:
        collection.delete(ids=existing_ids)

    embeddings = embedding_model.encode(chunks).tolist()

    ids = [
        f"{document_name}_{i}"
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=[
            {
                "source": document_name,
                "chunk": i
            }
            for i in range(len(chunks))
        ],
    )

    return len(chunks)
# -----------------------------
# Search documents
# -----------------------------
def search_documents(query, top_k=3):

    query_embedding = embedding_model.encode(
        [query]
    )[0].tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    return results

def get_indexed_documents():
    """Return uploaded documents reconstructed from ChromaDB metadata."""
    results = collection.get(include=["metadatas"])

    metadatas = results.get("metadatas", []) or []

    documents = {}

    for metadata in metadatas:
        if not metadata:
            continue

        source = metadata.get("source")

        if not source:
            continue

        if source not in documents:
            documents[source] = {
                "name": source,
                "chunks": 0
            }

        documents[source]["chunks"] += 1

    return list(documents.values())