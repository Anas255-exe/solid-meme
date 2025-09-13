
from fastapi import FastAPI
from src.loader import load_codebase
from src.analyzer import analyze_file, Issue
from src.reporter import summarize_report
from src.chat import build_vector_store, answer_query
from src.trend import save_trend, print_trend

app = FastAPI(title="Code Quality Intelligence Agent API")

@app.get("/")
def root():
    return {"message": "Welcome to the Code Quality Intelligence Agent API 🚀"}

@app.post("/analyze")
def analyze(path: str):
    files = load_codebase(path)
    all_issues = []
    all_issues_dict = []
    for file_path, content in files.items():
        issues = analyze_file(file_path, content[:2000])
        all_issues.extend(issues)
        all_issues_dict.extend([issue.__dict__ for issue in issues])
    save_trend(all_issues)
    return {"issues": all_issues_dict}

@app.post("/report")
def report(path: str):
    files = load_codebase(path)
    all_issues = []
    for file_path, content in files.items():
        issues = analyze_file(file_path, content[:2000])
        all_issues.extend(issues)
    save_trend(all_issues)
    # summarize_report prints to console, so you may want to adapt it to return a string or dict
    return {"total_issues": len(all_issues)}

@app.post("/chat")
def chat(path: str, query: str):
    vs = build_vector_store(path)
    return {"answer": answer_query(vs, query)}

@app.get("/trend")
def trend():
    print_trend()
    return {"trend": "Trend printed to console."}
