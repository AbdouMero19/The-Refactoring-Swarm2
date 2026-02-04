# src/utils/context.py
import ast
import os
from typing import Dict

def get_file_signatures(code_content: str) -> str:
    """Extracts signatures, including __init__ attributes."""
    try:
        tree = ast.parse(code_content)
    except SyntaxError:
        return "Error parsing."
    
    signatures = []
    
    def get_arg_type(arg) -> str:
        arg_name = arg.arg
        if arg.annotation:
            return f"{arg_name}: {ast.unparse(arg.annotation)}"
        return arg_name
    
    def get_return_type(node) -> str:
        if node.returns:
            return f" -> {ast.unparse(node.returns)}"
        return ""
    
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            signatures.append(f"class {node.name}:")
            
            # 1. Capture Class Attributes (The ones you already had)
            for item in node.body:
                if isinstance(item, ast.AnnAssign):
                    attr_name = item.target.id if isinstance(item.target, ast.Name) else "?"
                    annotation = ast.unparse(item.annotation)
                    signatures.append(f"    {attr_name}: {annotation}")
                elif isinstance(item, ast.Assign) and not isinstance(item, ast.FunctionDef):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            signatures.append(f"    {target.id}")

            # 2. Capture Methods AND Instance Attributes (The missing piece)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    args = [get_arg_type(a) for a in item.args.args]
                    return_type = get_return_type(item)
                    signatures.append(f"    def {item.name}({', '.join(args)}){return_type}")
                    
                    # 🎯 CRITICAL FIX: Look inside __init__ for self.x
                    if item.name == "__init__":
                        for stmt in item.body:
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    # Check for self.attribute = ...
                                    if isinstance(target, ast.Attribute) and \
                                       isinstance(target.value, ast.Name) and \
                                       target.value.id == "self":
                                        signatures.append(f"        self.{target.attr}")
                                        
        elif isinstance(node, ast.FunctionDef):
            args = [get_arg_type(a) for a in node.args.args]
            return_type = get_return_type(node)
            signatures.append(f"def {node.name}({', '.join(args)}){return_type}")

    return "\n".join(signatures)

def get_single_file_signature(filename:str ,content: str) -> str:
    """Reads file from disk and returns formatted string."""
    try:
        sigs = get_file_signatures(content)
        return f"File: {os.path.basename(filename)}\n{sigs}\n{'-'*30}"
    except Exception:
        return ""
    
def build_project_context(file_paths: list) -> Dict[str, str]:
    """Scans all files and builds a dictionary with filenames as keys and signatures as values."""
    context_dict = {}
    
    for path in file_paths:
        filename = os.path.basename(path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            sigs = get_file_signatures(content)
            context_dict[filename] = sigs
        except Exception:
            pass
            
    return context_dict    