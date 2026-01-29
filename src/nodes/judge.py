import subprocess
import os
import re
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Command
from langgraph.graph import END
from src.state.AgentState import AgentState
from src.models.gemini_models import get_llm
from src.utils.pylint_tool import run_pylint
from src.prompts.judge_prompts import (
    GEN_TEST_SYSTEM_PROMPT, get_gen_test_user_prompt,
    FORMALIZE_SYSTEM_PROMPT, get_formalize_user_prompt
)

def judge_node(state: AgentState) -> Command[Literal["AUDITOR", END]]:
    filename = state["filename"]
    code_content = state["code_content"]
    iteration = state.get("iteration_count", 0)
    base_name = os.path.basename(filename)
    dir_name = os.path.dirname(filename)
    test_filename = os.path.join(dir_name, f"test_{base_name}")

    print(f"⚖️ Judge: Evaluating {base_name}...")

    # --- PHASE 1: GENERATE TESTS ---
    llm = get_llm(model_type="pro")
    gen_response = llm.invoke([
        SystemMessage(content=GEN_TEST_SYSTEM_PROMPT),
        HumanMessage(content=get_gen_test_user_prompt(base_name, code_content))
    ])
    
    code_match = re.search(r"```python(.*?)```", gen_response.content, re.DOTALL)
    test_code = code_match.group(1).strip() if code_match else gen_response.content
    
    with open(test_filename, "w" , encoding="utf-8") as f:
        f.write(test_code)

    # --- PHASE 2: RUN TESTS ---
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{state['project_root']}:{env.get('PYTHONPATH', '')}"

    try:
        result = subprocess.run(["pytest", test_filename], capture_output=True, text=True, timeout=10, env=env)
        passed = (result.returncode == 0)
        raw_output = result.stdout + result.stderr
    except Exception as e:
        passed = False
        raw_output = f"CRITICAL SYSTEM ERROR: {str(e)}"

    # --- PHASE 3: DECISION ---
    if passed:
        print("✅ Judge: Tests Passed.")
        pylint_res = run_pylint(filename)
        return Command(update={"pylint_score": pylint_res["score"], "test_errors": "Passed"}, goto=END)

    if iteration >= 3:
        print("🛑 Judge: Max retries reached.")
        pylint_res = run_pylint(filename)
        return Command(update={"pylint_score": pylint_res["score"]}, goto=END)

    # --- PHASE 4: FORMALIZE FEEDBACK ---
    print("❌ Judge: Tests Failed. Formalizing feedback...")
    analysis = llm.invoke([
        SystemMessage(content=FORMALIZE_SYSTEM_PROMPT),
        HumanMessage(content=get_formalize_user_prompt(base_name, raw_output))
    ])
    
    return Command(
        update={
            "test_errors": analysis.content,
            "iteration_count": iteration + 1,
            "messages": [HumanMessage(content=f"Judge: Tests failed. Feedback: {analysis.content}")]
        },
        goto="AUDITOR"
    )
