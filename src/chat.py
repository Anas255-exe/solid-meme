import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
import google.generativeai as genai
from src.loader import load_codebase
from rich.console import Console

# ---------------- Config ----------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Embedding & Generation models
EMBED_MODEL = "models/text-embedding-004"
GENERATE_MODEL = "gemini-2.0-flash"
console = Console()

# ---------------- System Prompt ----------------
SYSTEM_PROMPT = """
You are CodeAssist, an AI code quality copilot.
Your goals:
- Be helpful, precise, and concise in your answers.
- Attribute findings to specific files or functions.
- When uncertain, admit uncertainty with "⚠️ Not enough information in codebase."
- Always explain reasoning step-by-step, but in plain text aligned to a terminal interface (no markdown formatting, no bold, no backticks).
- Preserve developer trust: NEVER hallucinate files/functions that don’t exist in the given context.
- Maintain a neutral, professional tone.

Remember the spirit of Claude’s system prompt research:
- Be transparent about what you know/don’t know.
- Stay on-topic.
- Avoid decorative output; clarity and accuracy matter most for developers in a terminal interface.
"""

# ---------------- Build Vector Store ----------------
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

# ---------------- Answer Query ----------------
def answer_query(collection, query: str):
    """Embed query, retrieve context from Chroma, and get answer from Gemini."""
    query_embedding = genai.embed_content(model=EMBED_MODEL, content=query)["embedding"]

    results = collection.query(query_embeddings=[query_embedding], n_results=4)

    if not results["documents"] or len(results["documents"][0]) == 0:
        return "⚠️ Not enough information in codebase."

    # Assemble context with file attribution
    context_parts = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        file = meta["file"]
        context_parts.append(f"File: {file}\n{doc}")
    context = "\n\n".join(context_parts)

    # Final composed prompt
    prompt = f"""
{SYSTEM_PROMPT}

User Question:
{query}

Relevant Code Context:
{context}

Developer-facing Answer (plain text, no markdown):
"""

    model = genai.GenerativeModel(GENERATE_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()

# ---------------- Interactive Chat Loop ----------------
def start_chat(path: str):
    """
    Interactive chat session over codebase (RAG + meta commands).
    Doesn't affect other CLI commands.
    """
    console.print(f"💬 Building RAG index for {path} ...", style="cyan")
    collection = build_vector_store(path)
    console.print("✅ Chat session ready. Ask questions or use commands (!analyze, !trend). Type 'exit' to quit.\n", style="green")

    while True:
        query = input("> ").strip()
        if query.lower() in ["exit", "quit", "q"]:
            console.print("👋 Exiting chat session.", style="yellow")
            break

        # Meta-commands: handled only in chat loop, won’t affect other endpoints
        if query.startswith("!analyze"):
            console.print("🔍 (Meta) You asked to run analyze/report. Run it separately via CLI if needed.", style="cyan")
            continue
        if query.startswith("!trend"):
            console.print("📊 (Meta) You asked for trend analysis. Run 'python main.py trend' in CLI.", style="cyan")
            continue
        
        # Default → natural Q&A
        answer = answer_query(collection, query)
        console.print(f"🤖 {answer}\n", style="white")