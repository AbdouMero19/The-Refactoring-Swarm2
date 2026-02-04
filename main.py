import argparse
import sys
import os
import shutil
import glob
import uuid
from dotenv import load_dotenv
from importlib_metadata import files
from langchain_core.messages import HumanMessage

# Import your custom modules
from src.utils.logger import log_experiment
from src.state.AgentState import AgentState
from src.graph.graph import build_agent_graph
from time import sleep
from src.utils.black import run_black
from src.utils.context import build_project_context
from src.utils.batching import build_sequential_batches

load_dotenv()

# Configuration
SANDBOX_ROOT = "./sandbox"

def setup_project_sandbox(target_dir: str) -> str:
    """
    Mirrors the target directory into a clean sandbox environment.
    Returns the path to the new sandboxed project root.
    """
    # 1. Create sandbox root if it doesn't exist
    if not os.path.exists(SANDBOX_ROOT):
        os.makedirs(SANDBOX_ROOT)

    project_name = os.path.basename(os.path.normpath(target_dir))
    
    # 2. Create a unique ID for this run to avoid collisions
    run_id = str(uuid.uuid4())[:8]
    sandbox_path = os.path.join(SANDBOX_ROOT, f"{project_name}_{run_id}")
    
    # 3. Copy the ENTIRE folder tree
    # This preserves local imports (e.g., from utils import helper)
    if os.path.exists(sandbox_path):
        shutil.rmtree(sandbox_path)
        
    shutil.copytree(target_dir, sandbox_path)
    
    # log_experiment("System", "SANDBOX", f"Mirrored {target_dir} -> {sandbox_path}", "INFO")
    return sandbox_path

def main():
    # 1. Parse Arguments
    parser = argparse.ArgumentParser(description="AI Refactoring Agent")
    parser.add_argument("--target_dir", type=str, required=True, help="Path to the folder containing code to fix")
    args = parser.parse_args()

    # 2. Validation
    if not os.path.exists(args.target_dir):
        print(f"❌ Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    print(f"🚀 DEMARRAGE SUR : {args.target_dir}")
    # log_experiment("System", "STARTUP", f"Target: {args.target_dir}", "INFO")

    # 3. Setup Sandbox (Critical Safety Step)
    try:
        sandboxed_dir = setup_project_sandbox(args.target_dir)
        print(f"📦 Sandbox créé: {sandboxed_dir}")
    except Exception as e:
        print(f"❌ Erreur création sandbox: {e}")
        # log_experiment("System", "CRITICAL", f"Sandbox creation failed: {e}", "ERROR")
        sys.exit(1)
        
       

    # 4. Find Files
    # We scan the SANDBOX, not the original directory
    # recursive=True ensures we find files in subfolders
    files = glob.glob(os.path.join(sandboxed_dir, "**", "*.py"), recursive=True)
    
    # Filter out common non-target files
    # files = [f for f in files if "test_" not in f and "setup.py" not in f and "__init__.py" not in f]

    print(f"📂 Found {len(files)} python files to process.")
    
    
    # 5. Build & Compile Graph
    # We build the graph once and reuse it for all files
    builder = build_agent_graph()
    graph = builder.compile()
    
      
    # 6. Execution Loop
    for batch in build_sequential_batches(files):
        # 1. Prepare Batch Metadata
        # Convert absolute paths (sandbox) to relative paths for display/agent
        # e.g. ["/abs/sandbox/inventory.py", "/abs/sandbox/order.py"]
        
        batch_relative_paths = [os.path.relpath(f, sandboxed_dir) for f in batch]
        
        # Create the string signature: "inventory.py | order.py"
        files_paths_str = " | ".join(batch_relative_paths)
        
        print(f"\n{'='*60}")
        print(f"👉 Processing Batch: {files_paths_str}")
        print(f"{'='*60}")

        # 2. Prepare Code Content (Concatenate all files in batch)
        full_code_content = ""
        valid_batch = True
        
        for file_path, relative_name in zip(batch, batch_relative_paths):
            print(f"   🔍 Formatting {relative_name}...")
            run_black(file_path)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    full_code_content += f"FILE: {relative_name}\n"
                    full_code_content += f.read() + "\n\n"
            except Exception as e:
                print(f"❌ Failed to read {relative_name}: {e}")
                valid_batch = False
                break
        
        if not valid_batch: continue

        try:
            # 3. Initialize Agent State
            initial_state = {
                "messages": [HumanMessage(content=f"Starting analysis on {files_paths_str}")],
                "filename": files_paths_str,      # Clean string "a.py | b.py"
                "project_root": sandboxed_dir,    # Critical for imports
                "code_content": full_code_content,
                "pylint_score": 0.0,
                "pylint_msg": "",
                "test_errors": "",
                "iteration_count": 0,
                # Pass ALL files in sandbox to context, so the agent knows about files outside the current batch
                "signatures_map": build_project_context(files), 
                "test_file": ""
            }

            # 4. RUN THE AGENT
            final_state = graph.invoke(initial_state)

            # 5. Reporting
            final_score = final_state.get("pylint_score", 0)
            print(f"✅ Finished Batch {files_paths_str}")
            print(f"   - Final Score: {final_score}/10")

        except Exception as e:
            print(f"❌ Failed on batch {files_paths_str}: {e}")
        
        print('sleeping for 4 seconds...')
        sleep(4)    

    print("\n✅ MISSION_COMPLETE")
    print(f"Output available in: {sandboxed_dir}")

if __name__ == "__main__":
    main()