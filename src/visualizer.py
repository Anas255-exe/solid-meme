import os
import re
import networkx as nx
import matplotlib.pyplot as plt

def extract_python_imports(code: str):
    """Extract Python imports (internal + external)."""
    imports = []
    for line in code.splitlines():
        line = line.strip()
        if line.startswith("import "):
            parts = line.replace("import", "").strip().split(",")
            imports.extend([p.strip().split()[0] for p in parts])
        elif line.startswith("from "):
            module = line.split()[1]
            imports.append(module.split(".")[0])
    return list(set(imports))

def extract_js_imports(code: str):
    """Extract JS/Node imports (ES6 & CommonJS)."""
    imports = []
    for line in code.splitlines():
        line = line.strip()
        if line.startswith("import "):
            match = re.search(r'from\s+[\'"]([^\'"]+)[\'"]', line)
            if match:
                imports.append(match.group(1).split("/")[0])
        elif "require(" in line:
            match = re.search(r'require\([\'"]([^\'"]+)[\'"]\)', line)
            if match:
                imports.append(match.group(1).split("/")[0])
    return list(set(imports))

def scan_dependencies(directory: str):
    """Scan all files in a repo for Python + JS dependencies."""
    dependencies = {}
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith((".py", ".js")):
                file_path = os.path.join(root, f)
                try:
                    code = open(file_path, encoding="utf-8").read()
                except:
                    continue

                if f.endswith(".py"):
                    deps = extract_python_imports(code)
                else:
                    deps = extract_js_imports(code)

                dependencies[file_path] = deps
    return dependencies

def create_dependency_graph(dependencies, output_file="dependency_graph.png"):
    """Create and save a dependency graph from dependencies."""
    G = nx.DiGraph()

    for file, deps in dependencies.items():
        for dep in deps:
            G.add_edge(file, dep)

    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=0.5, iterations=30)
    nx.draw(G, pos, with_labels=True, node_size=2500, node_color="lightblue", font_size=8, font_weight="bold", edge_color="gray")
    plt.savefig(output_file, bbox_inches="tight")
    plt.close()

def generate_dependency_graph(path: str):
    """Main entry point called by reporter.py"""
    dependencies = scan_dependencies(path)
    if dependencies:
        create_dependency_graph(dependencies)
        return True
    return False
