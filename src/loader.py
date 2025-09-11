import os
from pathlib import Path
from typing import Dict

def load_codebase(path: str, extensions=[".py", ".js"]) -> Dict[str, str]:
    """
    Loads source code files from a given path.
    - If path is a directory -> recursively load all code files.
    - If path is a single file -> only load that file (if extension matches).
    
    Args:
        path (str): Path to a file or directory
        extensions (list): List of extensions allowed (default = .py, .js)

    Returns:
        Dict[str, str]: {file_path: file_content}
    """
    base_path = Path(path)
    if not base_path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    
    files_content = {}

    if base_path.is_file():
        # Handle single file
        if base_path.suffix.lower() in extensions:
            try:
                with open(base_path, "r", encoding="utf-8", errors="ignore") as f:
                    files_content[str(base_path)] = f.read()
            except Exception as e:
                print(f"⚠️ Could not read {base_path}: {e}")
        else:
            print(f"❌ Skipping {base_path}, extension not supported")
    else:
        # Handle directory (previous behavior)
        for ext in extensions:
            for file_path in base_path.rglob(f"*{ext}"):
                if "venv" in str(file_path) or "node_modules" in str(file_path):
                    continue
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        files_content[str(file_path)] = f.read()
                except Exception as e:
                    print(f"⚠️ Could not read {file_path}: {e}")
    
    return files_content