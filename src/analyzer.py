import os
import json
import re
import ast
from typing import List
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv
# from src.analyzer import Issue  # reuse existing Issue schema if already defined
class Issue(BaseModel):
    file_path: str
    category: str = Field(description="Type of issue: security, performance, docs, complexity, etc.")
    issue_summary: str = Field(description="A one-sentence summary")
    detailed_explanation: str = Field(description="Detailed reasoning about why it's an issue")
    suggested_fix: str = Field(description="How to fix the issue")
    severity: str = Field(description="Low, Medium, or High")

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# -------------------- AST Static Analysis --------------------
def analyze_with_ast(file_path: str, file_content: str) -> List[Issue]:
    """
    Perform static analysis using Python AST for complexity/maintainability issues.
    Returns a list of Issue objects.
    Only applies to .py files.
    """
    issues = []
    if not file_path.endswith(".py"):
        return issues  # skip non-Python files

    try:
        tree = ast.parse(file_content)
    except SyntaxError as e:
        issues.append(Issue(
            file_path=file_path,
            category="Complexity",
            issue_summary="Syntax Error in Python code",
            detailed_explanation=str(e),
            suggested_fix="Fix syntax issues so the file can be parsed.",
            severity="High"
        ))
        return issues

    class FunctionAnalyzer(ast.NodeVisitor):
        def __init__(self):
            self.function_issues = []

        def visit_FunctionDef(self, node):
            # Count function length
            if hasattr(node, "body") and len(node.body) > 0:
                start = node.lineno
                end = node.body[-1].lineno if hasattr(node.body[-1], "lineno") else start
                length = end - start
                if length > 50:
                    self.function_issues.append(Issue(
                        file_path=file_path,
                        category="Complexity",
                        issue_summary=f"Function '{node.name}' too long ({length} lines)",
                        detailed_explanation=f"The function '{node.name}' spans ~{length} lines, reducing maintainability.",
                        suggested_fix="Refactor into smaller helper functions.",
                        severity="Medium"
                    ))
            
            # Check nesting depth
            max_depth = self.get_nesting_level(node)
            if max_depth > 3:
                self.function_issues.append(Issue(
                    file_path=file_path,
                    category="Complexity",
                    issue_summary=f"Function '{node.name}' too deeply nested",
                    detailed_explanation=f"'{node.name}' has nesting level {max_depth}, making it hard to understand.",
                    suggested_fix="Refactor logic to reduce nesting (extract helpers, early returns).",
                    severity="Medium"
                ))

            self.generic_visit(node)

        def get_nesting_level(self, node, level=0):
            if not hasattr(node, "body"):
                return level
            depths = []
            for child in node.body:
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                    depths.append(self.get_nesting_level(child, level+1))
            return max(depths) if depths else level

    analyzer = FunctionAnalyzer()
    analyzer.visit(tree)

    return analyzer.function_issues


# -------------------- AI (Gemini) Analysis --------------------
def clean_json(raw_text: str) -> str:
    """
    Cleans Gemini output to extract valid JSON.
    Removes ```json ... ``` wrappers if present.
    """
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*", "", text)
        text = re.sub(r"```$", "", text)
        text = text.strip()
    return text


def analyze_with_gemini(file_path: str, file_content: str) -> List[Issue]:
    """
    Analyze code using Gemini and return detected issues.
    """
    prompt = f"""
    You are an expert code reviewer.
    Analyze the following code file: {file_path}

    Identify issues in **4 categories**:
    1. Security vulnerabilities
    2. Performance bottlenecks
    3. Documentation / Code Quality issues
    4. Maintainability / Complexity issues
    - Large functions (>50 lines) 
    - Deeply nested loops 
    - Overly complex methods or classes

    ⚠️ Output Rules:
    - ONLY output valid JSON.
    - The JSON MUST be a list of objects.
    - Each object must have:
    file_path, category, issue_summary, detailed_explanation, suggested_fix, severity.

    For 'category', pick strictly one of:
    ["Security", "Performance", "Docs", "Complexity"]

    CODE:
    {file_content}
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    raw_text = response.text or ""
    raw_text = clean_json(raw_text)

    try:
        data = json.loads(raw_text)
        issues = [Issue(**item) for item in data]
    except Exception as e:
        print(f"⚠️ JSON parsing failed for {file_path}: {e}\nRaw output:\n{raw_text[:500]}...")
        issues = []

    return issues
def auto_severity(issue: Issue) -> str:
    """
    Auto-adjust severity based on category + summary.
    Security → always HIGH
    Performance → at least MEDIUM
    Docs → usually LOW
    Complexity → Medium unless severe
    """
    cat = issue.category.lower()

    if "security" in cat:
        return "High"
    if "performance" in cat:
        return "Medium"
    if "complexity" in cat:
        # if "too long" or "too nested" → Medium, else Low
        if "too long" in issue.issue_summary.lower() or "nested" in issue.issue_summary.lower():
            return "Medium"
        return "Low"
    if "docs" in cat:
        return "Low"

    # fallback to whatever model said
    return issue.severity

# -------------------- Combined Analysis --------------------
def analyze_file(file_path: str, file_content: str) -> List[Issue]:
    """
    Combines static AST-based analysis + AI (Gemini) analysis.
    """
    issues = []

    # First: run AST static analysis
    issues.extend(analyze_with_ast(file_path, file_content))

    # Then: run Gemini AI analysis
    issues.extend(analyze_with_gemini(file_path, file_content))
    for issue in issues:
        issue.severity = auto_severity(issue)

    return issues
