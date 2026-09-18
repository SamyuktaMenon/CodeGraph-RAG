import os
import ast
from typing import List, Dict, Any

class PythonCodeParser:
    """
    Parses Python code to extract functions, classes, and their relationships.
    Uses the built-in `ast` module for simplicity, but could be extended to use `tree-sitter` for multi-language support.
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def parse_file(self, file_path: str) -> Dict[str, List[Dict[str, Any]]]:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {"nodes": [], "relationships": []}

        nodes = []
        relationships = []
        
        class ASTVisitor(ast.NodeVisitor):
            def __init__(self, filepath: str, file_content: str):
                self.filepath = filepath
                self.content = file_content
                self.current_class = None
                self.current_function = None

            def visit_ClassDef(self, node):
                code_segment = ast.get_source_segment(self.content, node) or ""
                
                nodes.append({
                    "type": "Class",
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "code": code_segment,
                    "file_path": self.filepath,
                    "line_number": node.lineno
                })
                prev_class = self.current_class
                self.current_class = node.name
                self.generic_visit(node)
                self.current_class = prev_class

            def visit_FunctionDef(self, node):
                node_type = "Method" if self.current_class else "Function"
                name = f"{self.current_class}.{node.name}" if self.current_class else node.name
                code_segment = ast.get_source_segment(self.content, node) or ""
                
                nodes.append({
                    "type": node_type,
                    "name": name,
                    "docstring": ast.get_docstring(node),
                    "code": code_segment,
                    "file_path": self.filepath,
                    "line_number": node.lineno
                })
                
                if self.current_class:
                    relationships.append({
                        "source": name,
                        "target": self.current_class,
                        "type": "BELONGS_TO"
                    })
                
                prev_func = self.current_function
                self.current_function = name
                self.generic_visit(node)
                self.current_function = prev_func

            def visit_Call(self, node):
                if self.current_function:
                    if isinstance(node.func, ast.Name):
                        called_name = node.func.id
                        relationships.append({
                            "source": self.current_function,
                            "target": called_name,
                            "type": "CALLS"
                        })
                    elif isinstance(node.func, ast.Attribute):
                        called_name = node.func.attr
                        relationships.append({
                            "source": self.current_function,
                            "target": called_name,
                            "type": "CALLS"
                        })
                self.generic_visit(node)

        visitor = ASTVisitor(file_path, content)
        visitor.visit(tree)
        
        return {"nodes": nodes, "relationships": relationships}

    def parse_repo(self) -> Dict[str, List]:
        all_nodes = []
        all_rels = []
        for root, dirs, files in os.walk(self.repo_path):
            # Exclude virtual environments and hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('venv', '__pycache__', 'node_modules')]
            
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    result = self.parse_file(file_path)
                    all_nodes.extend(result.get("nodes", []))
                    all_rels.extend(result.get("relationships", []))
        return {"nodes": all_nodes, "relationships": all_rels}

if __name__ == "__main__":
    parser = PythonCodeParser(".")
    result = parser.parse_repo()
    print(f"Extracted {len(result['nodes'])} entities and {len(result['relationships'])} relationships from the current directory.")