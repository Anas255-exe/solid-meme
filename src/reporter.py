from typing import List
from collections import defaultdict, Counter
from rich.console import Console
from src.analyzer import Issue
import google.generativeai as genai
import os
from dotenv import load_dotenv
from src import visualizer
from src.visualizer import generate_dependency_graph
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def summarize_with_gemini(file: str, issues: List[Issue]) -> str:
    """
    Uses Gemini to generate a natural language one-line summary for a file's issues.
    """
    if not issues:
        return f"{file} → No issues found."

    # Build compact issue summary
    sev_counts = Counter([i.severity for i in issues])
    cat_counts = Counter([i.category for i in issues])
    issue_list = [
        f"{i.severity} {i.category}: {i.issue_summary}"
        for i in issues[:5]  # limit context
    ]
    compact_text = "; ".join(issue_list)

    prompt = f"""
    You are a code quality auditor. Summarize issues found for the file {file} in 1-2 natural, human-readable sentences.
    Severity count = {dict(sev_counts)}.
    Categories count = {dict(cat_counts)}.
    Issues: {compact_text}
    Only output a clear sentence summary, no JSON or formatting.
    Mention the code file while mentioning issues.
    Before stating the summary state the severity and category counts.
    for example \main.py → 5 issues (1 high-risk; 3 medium; 1 low) | Categories: Performance(1),
Docs(2), Complexity(2)
    Format it properly leave spaces in between.
    """

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"{file} → {len(issues)} issues (fallback summary)."

# def summarize_report(all_issues: List[Issue],repo_path:str) -> None:
def summarize_report(all_issues: List[Issue], repo_path: str) -> None:
    """
    Repo-level summary with natural-language per-file description.
    """
    console = Console()

    if not all_issues:
        console.print("\n✅ No issues found in the repo!", style="bold green")
        return

    # Group issues per file
    issues_by_file = defaultdict(list)
    for issue in all_issues:
        issues_by_file[issue.file_path].append(issue)

    console.print(f"\n📑 File-wise Summaries", style="bold cyan")
    for file, issues in issues_by_file.items():
        sentence = summarize_with_gemini(file, issues)
        console.print(f"📝 {sentence}", style="white")

def summarize_report_with_graph(all_issues: List[Issue], repo_path: str) -> None:
    """
    Repo-level summary with dependency graph visualization.
    """
    summarize_report(all_issues, repo_path)
    console = Console()
    console.print(f"\n🔎 Scanning dependency graph for: {repo_path} (Languages: Python + JS)")
    if generate_dependency_graph(repo_path):
        console.print("🕸️ Dependency graph saved as dependency_graph.png", style="bold green")
    else:
        console.print("⚠️ No dependencies found to visualize.", style="bold yellow")
