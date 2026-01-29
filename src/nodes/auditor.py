from pathlib import Path
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage 
from langgraph.types import Command 
from src.state.AgentState import AgentState
from src.models.gemini_models import get_llm
from src.utils.pylint_tool import run_pylint 
from src.prompts.auditor_prompts import AUDITOR_SYSTEM_PROMPT, get_auditor_user_prompt

def auditor_node(state: AgentState) -> Command[Literal["FIXER", "JUDGE"]]:
    filename = state["filename"]
    print(f"🔍 Auditor scanning {filename} with Pylint...")

    pylint_result = run_pylint(filename)
    score = pylint_result["score"]
    raw_output = pylint_result["stdout"]
    
    THRESHOLD = 9.5

    if (score >= THRESHOLD and state["test_errors"] == ""):
        print(f"✅ Code is clean (Score: {score}). Skipping FIXER -> JUDGE.")
        return Command(
            update={
                "pylint_score": score,
                "pylint_msg": "Style is excellent.",
                "messages": [HumanMessage(content=f"Auditor: Code is clean ({score}/10).")]
            },
            goto="JUDGE"
        )

    print(f"⚠️ Score is {score}. Invoking LLM and sending to FIXER...")
    llm = get_llm(model_type="flash")
    
    response = llm.invoke([
        SystemMessage(content=AUDITOR_SYSTEM_PROMPT),
        HumanMessage(content=get_auditor_user_prompt(Path(filename).name, score, raw_output))
    ])

    return Command(
        update={
            "pylint_score": score,
            "style_issues": response.content,
            "messages": [HumanMessage(content=response.content)]
        },
        goto="FIXER"
    )