import argparse
import sys
import os
import shutil
import glob
import uuid
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Import your custom modules
from src.utils.agent_logger import log_system_startup, log_system_completion
from src.state.AgentState import AgentState
from src.graph.graph import build_agent_graph

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
    log_system_startup(args.target_dir)

    # 3. Build & Compile Graph
    # We build the graph once and reuse it for all files
    builder = build_agent_graph()
    graph = builder.compile()

    # 4. Setup Sandbox (Critical Safety Step)
    try:
        sandboxed_dir = setup_project_sandbox(args.target_dir)
        print(f"📦 Sandbox créé: {sandboxed_dir}")
    except Exception as e:
        print(f"❌ Erreur création sandbox: {e}")
        # log_experiment("System", "CRITICAL", f"Sandbox creation failed: {e}", "ERROR")
        sys.exit(1)

    # 5. Find Files
    # We scan the SANDBOX, not the original directory
    # recursive=True ensures we find files in subfolders
    files = glob.glob(os.path.join(sandboxed_dir, "**", "*.py"), recursive=True)
    
    # Filter out common non-target files
    # files = [f for f in files if "test_" not in f and "setup.py" not in f and "__init__.py" not in f]

    print(f"📂 Found {len(files)} python files to process.")

    # 6. Execution Loop
    successful = 0
    failed = 0
    
    for file_path in files:
        relative_name = os.path.relpath(file_path, sandboxed_dir)
        print(f"\n{'='*60}")
        print(f"👉 Processing: {relative_name}")
        print(f"{'='*60}")

        try:
            # Read content from the sandboxed file
            with open(file_path, "r", encoding="utf-8") as f:
                code_content = f.read()

            # Initialize Agent State
            # We must pass 'project_root' so the Judge handles imports correctly
            initial_state = {
                "messages": [HumanMessage(content=f"Starting analysis on {relative_name}")],
                "filename": file_path,          # Absolute path in sandbox
                "project_root": sandboxed_dir,  # Root for PYTHONPATH imports
                "code_content": code_content,
                "pylint_score": 0.0,
                "pylint_msg": "",
                "test_errors": "",
                "iteration_count": 0
            }

            # RUN THE AGENT
            # .invoke() blocks until the graph hits END
            final_state = graph.invoke(initial_state)

            # Reporting
            final_score = final_state.get("pylint_score", 0)
            print(f"✅ Finished {relative_name}")
            print(f"   - Final Pylint Score: {final_score}/10")
            successful += 1

        except Exception as e:
            print(f"❌ Failed on {relative_name}: {e}")
            failed += 1
    
    # Log completion summary
    log_system_completion(
        files_processed=len(files),
        successful=successful,
        failed=failed
    )

    print("\n✅ MISSION_COMPLETE")
    print(f"Output available in: {sandboxed_dir}")
    print(f"📝 Logs saved to: logs/experiment_data.json")

if __name__ == "__main__":
    main()