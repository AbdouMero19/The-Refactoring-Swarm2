from pathlib import Path
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage 
from langgraph.types import Command  # <--- The modern way to route
from src.state import AgentState
from src.models.gemini_models import get_llm
from src.utils.pylint_tool import run_pylint 

def auditor_node(state: AgentState) -> Command[Literal["FIXER", "JUDGE"]]:
    """
    1. Runs Pylint (Static).
    2. Decides whether to invoke the LLM.
    3. Routes to 'FIXER' (if dirty) or 'JUDGE' (if clean).
    """
    filename = state["filename"]
    print(f"🔍 Auditor scanning {filename} with Pylint...")

    # --- 1. STATIC CHECK (Fast & Free) ---
    pylint_result = run_pylint(filename)
    score = pylint_result["score"]
    raw_output = pylint_result["stdout"]
    
    # Define our standard of excellence
    THRESHOLD = 9.5

    # --- SCENARIO A: CODE IS CLEAN ---
    if (score >= THRESHOLD and state["test_errors"] == ""):
        print(f"✅ Code is clean (Score: {score}) and logic is clean. Skipping FIXER -> Going to JUDGE.")
        
        # We construct a Command that updates state AND jumps to the next node
        return Command(
            # Update the state (Whiteboard)
            update={
                "pylint_score": score,
                "pylint_msg": "Style is excellent.",
                "messages": [HumanMessage(content=f"Auditor: Code is clean ({score}/10).")]
            },
            # Control Flow: Skip the FIXER entirely!
            goto="JUDGE"
        )

    # --- SCENARIO B: CODE IS DIRTY ---
    print(f"⚠️ Score is {score}. Invoking LLM and sending to FIXER...")

    llm = get_llm(model_type="flash")
    
    # Prompt the LLM to translate raw Pylint noise into clear instructions
    prompt = f"""
    The Pylint score for '{Path(filename).name}' is {score}/10. 
    Here is the raw output:
    {raw_output}
    
    Analyze this. Output a concise list of instructions for a developer to fix these style issues.
    """
    
    response = llm.invoke([
        SystemMessage(content="You are a Senior Code Auditor."),
        HumanMessage(content=prompt)
    ])

    return Command(
        # Update the state with the FIXER's instructions
        update={
            "pylint_score": score,
            "style_issues": response.content,
            "messages": [HumanMessage(content=response.content)]
        },
        # Control Flow: Go to the FIXER to apply changes
        goto="FIXER"
    )