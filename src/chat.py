import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
import google.generativeai as genai
from src.loader import load_codebase

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Embedding model (for vector DB)
EMBED_MODEL = "models/text-embedding-004"

# Generation model (latest Gemini)
GENERATE_MODEL = "gemini-2.0-flash"


def build_vector_store(path: str):
    """Load repo, split into chunks, embed chunks, and store in Chroma."""
    code_files = load_codebase(path)
    docs = []

    for file_path, content in code_files.items():
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_text(content)
        for idx, chunk in enumerate(chunks):
            docs.append({
                "id": f"{file_path}-{idx}",
                "text": chunk,
                "metadata": {"file": file_path}
            })

    client = chromadb.Client()
    collection = client.create_collection("code_chunks")

    for d in docs:
        embedding = genai.embed_content(model=EMBED_MODEL, content=d["text"])
        emb = embedding["embedding"]
        collection.add(
            documents=[d["text"]],
            metadatas=[d["metadata"]],
            ids=[d["id"]],
            embeddings=[emb]
        )

    return collection


def answer_query(collection, query: str):
    """Embed query, retrieve context from Chroma, and get answer from Gemini."""
    query_embedding = genai.embed_content(model=EMBED_MODEL, content=query)["embedding"]

    results = collection.query(query_embeddings=[query_embedding], n_results=4)

    if not results["documents"] or len(results["documents"][0]) == 0:
        return "⚠️ Not enough information in codebase."

    # ✅ Include file metadata in context
    context_parts = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        file = meta["file"]
        context_parts.append(f"File: {file}\n{doc}")
    context = "\n\n".join(context_parts)

    model = genai.GenerativeModel(GENERATE_MODEL)
    prompt = f"""
    You are a helpful AI assistant analyzing a multi-file codebase.

    Question: {query}

    Code Context (with file origins labeled):
    {context}

    Instructions:
    - Always attribute details to the correct file(s).
    - If multiple files show relevant info, explain the roles of each one.
    - If no relevant info is found in context, reply: "⚠️ Not enough information in codebase."
    """

    response = model.generate_content(prompt)
    return response.text.strip()