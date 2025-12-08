#  Code Quality Intelligence Agent

An **AI-powered developer assistant** that analyzes code repositories, detects quality issues, generates actionable reports, visualizes trends, and even answers natural-language questions about your codebase.

It goes beyond simple linting by combining:

* **AST-based static analysis**
* **Large Language Model (Gemini)** for semantic reasoning
* **Retrieval-Augmented Generation (RAG)** for handling large repos
* **Developer-friendly visualizations** (charts, dependency graphs, trends)

---

## ✨ Features

* 🔍 **Code Quality Analysis** – Scan Python & JavaScript repos for quality issues
* 📑 **Reports** – Summaries with severity scoring & actionable fixes
* 🕸️ **Dependency Visualization** – Graphs showing file/module relationships
* 📊 **Trend Tracking** – Track regressions or improvements over time
* 💬 **Interactive Chat** – Natural-language Q\&A powered by RAG + LLM
* 🖥️ **CLI Interface** – Easy commands: `analyze`, `report`, `trend`, `chat`
* 🌐 **REST API (FastAPI)** – Endpoints: `/analyze`, `/report`, `/trend`, `/chat`
* ☁️ **Cloud Deployment** – Hosted on **Railway** with Swagger UI
---

## 📸 Architecture

<img width="1561" height="1020" alt="diagram-export-9-14-2025-11_18_59-AM" src="https://github.com/user-attachments/assets/2150bb93-0d57-4867-ab6c-a24db6ed9d91" />




---



The agent follows a **hybrid pipeline**:

* **Loader** → Reads files (Python/JS) from local path or GitHub repo
* **Analyzer** → AST parsing + static analysis + Gemini LLM evaluation
* **Reporter** → Generates summaries, charts, dependency graphs, and trend logs
* **Trend Tracker** → Compares previous runs for progress tracking
* **Chat (RAG)** → Conversational Q\&A over repo chunks
* **FastAPI Server** → Exposes CLI features as REST endpoints



---

## ⚙️ Installation

Clone the repo:

```bash
git clone https://github.com/Anas255-exe/solid-meme
cd code-quality-agent
```

Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Add Gemini API key:

```bash
echo "GEMINI_API_KEY=your-key" > .env
```

---

## 🖥️ Usage

### CLI Commands

```bash
# Analyze a repo
python main.py analyze <path-to-code>

# Generate reports
python main.py report

# Compare trends
python main.py trend

# Ask questions
python main.py chat
```

### REST API

Run locally:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

Deployed on Railway: `https://solid-meme-production.up.railway.app/docs`

**Endpoints:**

* `POST /analyze` – Analyze repo (local/GitHub)
* `GET /report` – Get summarized report
* `GET /trend` – Compare last two runs
* `POST /chat` – Ask natural-language questions

---

## 📊 Example Outputs

### CLI Report


<img width="1200" height="558" alt="image" src="https://github.com/user-attachments/assets/d1054db2-59a0-42f4-9bbb-e505e106846a" />


### Charts

<img width="1000" height="500" alt="image" src="https://github.com/user-attachments/assets/7daebdca-a09b-4d1c-a16c-143380cf4387" />



### Dependency Graph


<img width="1220" height="819" alt="image" src="https://github.com/user-attachments/assets/ea70abec-a4b5-4074-bba2-d2c7c42bb55c" />


---

## ⚙️ Engineering Decisions & Challenges

### 🔑 Key Decisions

* **Hybrid AST + LLM** → AST for structural precision, LLM for semantic reasoning
* **RAG for large repos** → prevents token overflow, keeps analysis scalable
* **Visualizations** → `matplotlib` + `networkx` for graphs and charts
* **Deployment on Railway** → lightweight FastAPI + Uvicorn for cloud access

### 🚧 Challenges & Solutions

* **Large repo handling** → solved with chunking + RAG retrieval
* **Free-tier constraints** → optimized Gemini API calls, lightweight outputs
* **Balancing speed & accuracy** → static analysis (fast) + LLM reasoning (deep)
* **Cloud limits** → tuned FastAPI for Railway resource caps

---

## 📌 Notes

* The **live Railway API** is available for **30 days** or until the **\$5 free credits** run out.
* Gemini API usage is **rate-limited**; heavy queries may cause bottlenecks.
* Best tested on **small-to-medium repos** for smooth performance.
* If the live API is unavailable, you can run the agent locally with the CLI.

---

## 🧩 Tech Stack

* **Python 3.10+**
* **LLM:** Google Gemini API (`google-generativeai`)
* **Frameworks:** FastAPI, Typer, LangChain (RAG)
* **Visualization:** matplotlib, networkx, pandas
* **Parsing/Analysis:** Python `ast`, `radon`, `pylint`, JS `eslint`
* **Deployment:** Railway (FastAPI + Uvicorn)

---

## 🙌 Acknowledgements

* [Google Gemini](https://ai.google.dev/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [LangChain](https://www.langchain.com/)
* [Matplotlib](https://matplotlib.org/)
* [NetworkX](https://networkx.org/)

---


