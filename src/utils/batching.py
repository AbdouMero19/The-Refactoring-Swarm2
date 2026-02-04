import ast
import re
import os

def get_imports_robust(file_path):
    """
    Extracts imported modules from a file.
    
    Strategy:
    1. Try parsing with AST (Abstract Syntax Tree). This is accurate and ignores 
       imports inside comments or strings.
    2. If AST fails (due to SyntaxError in the broken file), fall back to Regex.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    imports = set()

    # --- STRATEGY 1: AST (The Precise Way) ---
    try:
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            # Case A: import os, sys
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # 'alias.name' could be 'os.path'. We only want 'os'.
                    root_module = alias.name.split('.')[0]
                    imports.add(root_module)
            
            # Case B: from inventory import check_stock
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # 'node.module' is 'inventory'
                    root_module = node.module.split('.')[0]
                    imports.add(root_module)

        # If we successfully parsed the AST, we are done. Return immediately.
        return imports

    except SyntaxError:
        print(f"⚠️ Syntax Error detected in {file_path}. AST failed. Switching to Regex fallback.")
    except Exception as e:
        print(f"⚠️ Unexpected error parsing {file_path}: {e}. Switching to Regex fallback.")

    # --- STRATEGY 2: REGEX (The "Dirty" Fallback) ---
    # We only reach here if AST crashed. This is less accurate (might catch comments)
    # but guarantees we still get a dependency graph even if the code is broken.
    
    # Matches: from (inventory) import ...
    imports.update(re.findall(r'^\s*from\s+(\w+)', content, re.MULTILINE))
    
    # Matches: import (os)
    # This also catches "import os, sys" but only captures the first one cleanly in simple regex.
    # For a robust fallback, we iterate common patterns.
    imports.update(re.findall(r'^\s*import\s+(\w+)', content, re.MULTILINE))

    return imports

def build_sequential_batches(files):
    # 1. Build the Dependency Map with FULL PATHS
    # dependency_map = { "./path/to/order.py": {'inventory'} }
    dependency_map = {f: get_imports_robust(f) for f in files}
    
    # 2. Build a "Lookup Bridge" to fix the Path Mismatch
    # Maps "product.py" -> "./sandbox/.../product.py"
    filename_to_fullpath = {os.path.basename(f): f for f in files}
    
    batches = []
    
    while dependency_map:
        # 1. Find Ready Files
        ready_files = []
        for f, deps in dependency_map.items():
            # Check if any dependency 'd' corresponds to a file in our remaining list
            # We use the BRIDGE to convert 'product' -> 'product.py' -> full path
            has_dependency = False
            for d in deps:
                dep_filename = d + ".py"
                
                # If this dependency exists in our project AND is still in the map
                if dep_filename in filename_to_fullpath:
                    full_dep_path = filename_to_fullpath[dep_filename]
                    if full_dep_path in dependency_map:
                        has_dependency = True
                        break
            
            if not has_dependency:
                ready_files.append(f)
        
        if ready_files:
            # Sort to ensure consistent behavior
            ready_files.sort()
            
            # OPTION A: Clean Files Found -> Pick ONE (Sequential Mode)
            next_file = ready_files[0]
            batches.append([next_file])
            del dependency_map[next_file]
            continue 

        # 2. OPTION B: No Ready Files -> Cycle Detected
        start_node = next(iter(dependency_map)) 
        cycle_batch = set()
        stack = [start_node]
        
        while stack:
            current = stack.pop()
            if current in cycle_batch: continue
            cycle_batch.add(current)
            
            for d in dependency_map[current]:
                dep_filename = d + ".py"
                if dep_filename in filename_to_fullpath:
                    full_dep_path = filename_to_fullpath[dep_filename]
                    if full_dep_path in dependency_map:
                        cycle_batch.add(full_dep_path)
                        stack.append(full_dep_path)
        
        batches.append(list(cycle_batch))
        
        for f in cycle_batch:
            if f in dependency_map:
                del dependency_map[f]

    return batches