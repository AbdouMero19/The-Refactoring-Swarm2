from pathlib import Path
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage 
from langgraph.types import Command 
from src.state.AgentState import AgentState
from src.models.AI_models import get_llm
from src.utils.pylint_tool import run_pylint 
from src.prompts.auditor_prompts import AUDITOR_SYSTEM_PROMPT, get_auditor_user_prompt

def auditor_node(state: AgentState) -> Command[Literal["FIXER", "JUDGE"]]:
    """
    1. Runs Pylint (Static).
    2. Decides whether to invoke the LLM.
    3. Routes to 'FIXER' (if dirty) or 'JUDGE' (if clean).
    """
    filename = state["filename"]
    target_dir = state["project_root"]
    print(f"🔍 Auditor scanning {filename} with Pylint...")

    file_list = [f"{target_dir}/{f.strip()}" for f in filename.split("|")]
    pylint_result = run_pylint(file_list)
    score = pylint_result["score"]
    raw_output = pylint_result["stdout"]
    
    THRESHOLD = 9.25
    # --- SCENARIO A: CODE IS CLEAN ---
    if (score >= THRESHOLD and state["test_errors"] == ""):
        print(f"✅ Code is clean (Score: {score}). Skipping FIXER.")
        return Command(
            update={
                "pylint_score": score,
                "messages": [HumanMessage(content=f"Auditor: Code is clean ({score}/10).")]
            },
            goto="JUDGE"
        )
    if (score >= THRESHOLD):
        print(f"⚠️ Score is {score}.")
        return Command(
            update={
                "pylint_score": score,
                "messages": [HumanMessage(content=f"Auditor: Code is clean ({score}/10).")]
            },
            goto="FIXER"
        )    
# --- SCENARIO B: CODE IS DIRTY ---
    print(f"⚠️ Score is {score}. Invoking LLM")
    llm = get_llm(model_type="small")
    
    response = llm.invoke([
        SystemMessage(content=AUDITOR_SYSTEM_PROMPT),
        HumanMessage(content=get_auditor_user_prompt(Path(filename).name, score, raw_output))
    ])

    print(f"sending to FIXER...")
    return Command(
        update={
            "pylint_score": score,
            "style_issues": response.content,
            "messages": [HumanMessage(content=response.content)]
        },
        goto="FIXER"
    )