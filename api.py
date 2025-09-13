import tempfile
import shutil
import os
import subprocess
from fastapi import FastAPI, HTTPException
from src.loader import load_codebase
from src.analyzer import analyze_file, Issue
from src.reporter import summarize_report
from src.chat import build_vector_store, answer_query
from src.trend import save_trend, print_trend

app = FastAPI(title="Code Quality Intelligence Agent API")

def clone_github_repo(repo_url: str) -> str:
    temp_dir = tempfile.mkdtemp()
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, temp_dir],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        shutil.rmtree(temp_dir)
        raise HTTPException(status_code=400, detail=f"Git clone failed: {e.stderr.decode()}")
    return temp_dir

@app.get("/")
def root():
    return {"message": "Welcome to the Code Quality Intelligence Agent API 🚀"}

@app.post("/analyze")
def analyze(repo_url: str):
    temp_dir = clone_github_repo(repo_url)
    try:
        files = load_codebase(temp_dir)
        all_issues = []
        all_issues_dict = []
        for file_path, content in files.items():
            issues = analyze_file(file_path, content[:2000])
            all_issues.extend(issues)
            all_issues_dict.extend([issue.__dict__ for issue in issues])
        save_trend(all_issues)
        return {"issues": all_issues_dict}
    finally:
        shutil.rmtree(temp_dir)

@app.post("/report")
def report(repo_url: str):
    temp_dir = clone_github_repo(repo_url)
    try:
        files = load_codebase(temp_dir)
        all_issues = []
        for file_path, content in files.items():
            issues = analyze_file(file_path, content[:2000])
            all_issues.extend(issues)
        save_trend(all_issues)
        return {"total_issues": len(all_issues)}
    finally:
        shutil.rmtree(temp_dir)

@app.post("/chat")
def chat(repo_url: str, query: str):
    temp_dir = clone_github_repo(repo_url)
    try:
        vs = build_vector_store(temp_dir)
        return {"answer": answer_query(vs, query)}
    finally:
        shutil.rmtree(temp_dir)

@app.get("/trend")
def trend():
    print_trend()
    return {"trend": "Trend printed to console."}
