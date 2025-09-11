import typer
from src.loader import load_codebase

from src.analyzer import analyze_file

app = typer.Typer(help="AI Code Quality Intelligence Agent")

from src.analyzer import analyze_file, Issue
from rich.console import Console
from rich.table import Table
from src.loader import load_codebase
# from src.analyzer import analyze_file
from src.reporter import summarize_report
# from rich.console import Console
from src.chat import build_vector_store, answer_query

@app.command()
def chat(path: str):
    """
    Interactive Q&A about the repo using RAG (Retrieval Augmented Generation).
    """
    console = Console()
    console.print(f"💬 Building RAG index for {path} ...", style="cyan")
    collection = build_vector_store(path)
    console.print("✅ Ready. Type your questions (type 'exit' to quit)\n", style="green")

    while True:
        query = input("> ")
        if query.lower() in ["exit", "quit", "q"]:
            console.print("👋 Exiting chat.", style="yellow")
            break

        answer = answer_query(collection, query)
        console.print(f"🤖 {answer}\n", style="white")

@app.command()
def report(path: str):
    """
    Generate ONLY a summary report of the repo (skip per-file details).
    """
    console = Console()
    console.print(f"📊 Generating summary report for: {path}", style="bold cyan")

    code_files = load_codebase(path)
    console.print(f"✅ Loaded {len(code_files)} files", style="green")

    all_issues = []
    for file_path, content in code_files.items():
        issues = analyze_file(file_path, content[:2000])  # analyze quietly
        all_issues.extend(issues)

    # ✅ Print just the summary
    summarize_report(all_issues)

@app.command()
def analyze(path: str):
    """
    Analyze a codebase at the given path.
    """
    console = Console()
    console.print(f"🔍 Analyzing codebase at: {path}", style="bold cyan")

    code_files = load_codebase(path)
    console.print(f"✅ Loaded {len(code_files)} files", style="green")

    for file_path, content in code_files.items():
        console.print(f"\n📄 Reviewing {file_path}...", style="yellow")
        issues = analyze_file(file_path, content[:2000])  # trimming large files for now

        if not issues:
            console.print("   ✅ No structured issues found", style="dim")
            continue
        
        table = Table(title=f"Issues in {file_path}")
        table.add_column("Category", style="bold blue")
        table.add_column("Severity")
        table.add_column("Summary", style="bold white")
        table.add_column("Suggested Fix", style="green")

        for issue in issues:
            # Add severity coloring
            sev_color = "red" if issue.severity == "High" else "yellow" if issue.severity == "Medium" else "green"
            table.add_row(issue.category, f"[{sev_color}]{issue.severity}[/{sev_color}]", issue.issue_summary, issue.suggested_fix)

        console.print(table)


if __name__ == "__main__":
    app()