import os
from typing import List
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class Issue(BaseModel):
    file_path: str
    category: str = Field(description="Type of issue: security, performance, docs, complexity, etc.")
    issue_summary: str = Field(description="A one-sentence summary")
    detailed_explanation: str = Field(description="Detailed reasoning about why it's an issue")
    suggested_fix: str = Field(description="How to fix the issue")
    severity: str = Field(description="Low, Medium, or High")

def clean_json(raw_text: str) -> str:
    """
    Cleans Gemini output to extract valid JSON.
    Removes ```json ... ``` wrappers if present.
    """
    # Remove leading/trailing whitespace
    text = raw_text.strip()

    # If wrapped in ```json blocks, extract between them
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*", "", text)   # remove opening ```json or ```
        text = re.sub(r"```$", "", text)            # remove closing ```
        text = text.strip()

    return text

def analyze_file(file_path: str, file_content: str) -> List[Issue]:
    """
    Analyze a single file with Gemini and return detected issues.
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

    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    response = model.generate_content(prompt)

    raw_text = response.text or ""
    raw_text = clean_json(raw_text)   # ✅ clean before parsing

    try:
        data = json.loads(raw_text)
        issues = [Issue(**item) for item in data]
    except Exception as e:
        print(f"⚠️ JSON parsing failed for {file_path}: {e}\nRaw output:\n{raw_text[:500]}...")
        issues = []

    return issues