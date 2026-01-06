import argparse
import sys
import os
from dotenv import load_dotenv
from src.utils.logger import log_experiment, ActionType
from src.auditor import auditor_node

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True)
    args = parser.parse_args()

    if not os.path.exists(args.target_dir):
        print(f"❌ Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    print(f"🚀 DEMARRAGE SUR : {args.target_dir}")
    
    # 2. INITIALIZE THE STATE
    state = {
        "messages": [],
        "target_dir": args.target_dir,
        "analysis_report": "",
        "refactoring_plan": "",
        "iteration_count": 0
    }
    
    # 3. CALL THE AUDITOR NODE
    # This is where the actual LLM call and Pylint analysis happen
    print("🤖 Appeler l'Auditeur...")
    final_state = auditor_node(state)
    
    # 4. SHOW THE RESULTS IN TERMINAL
    print("\n--- RAPPORT D'ANALYSE ---")
    print(final_state["analysis_report"])
    print("\n--- PLAN DE REFACTORING ---")
    print(final_state["refactoring_plan"])

    print("\n✅ MISSION_COMPLETE")

if __name__ == "__main__":
    main()
    
    