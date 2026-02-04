import os
import re
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Command
from langgraph.graph import END
from src.state.AgentState import AgentState
from src.models.AI_models import get_llm
from src.utils.pylint_tool import run_pylint
from src.utils.pytest_tool import run_pytest
from src.utils.file_tool import write_file
from src.utils.logger import log_experiment, ActionType
from time import sleep
from pathlib import Path
from src.prompts.judge_prompts import (
    GEN_TEST_SYSTEM_PROMPT, get_gen_test_user_prompt,
    FORMALIZE_SYSTEM_PROMPT, get_formalize_user_prompt
)


def judge_node(state: AgentState) -> Command[Literal["AUDITOR", END]]:
    """
    1. GENERATE TESTS: Writes a specific test file for the code.
    2. RUN TESTS: Executes pytest.
    3. ANALYZE (If Fail): Uses LLM to summarize exactly what went wrong.
    4. DECIDE: Pass -> End | Fail -> AUDITOR.
    """
    sleep(4)  # To avoid rate limits
    filename = state["filename"]
    code_content = state["code_content"]
    target_dir = state["project_root"]
    iteration = state.get("iteration_count", 0)

    # Setup paths
    base_name = filename

    test_content = state["test_file"]
    
    print(f"⚖️ Judge: Evaluating {base_name}...")

    if (test_content=="") : 
    
        print("Generating test file...")
        # --- PHASE 1: GENERATE TESTS ---
        llm_no_tools = get_llm(model_type="large")
        llm = llm_no_tools.bind_tools([write_file])
        
        gen_system_msg = GEN_TEST_SYSTEM_PROMPT
        gen_user_msg = get_gen_test_user_prompt(base_name, code_content, signatures_map=state["signatures_map"].values())
        
        gen_response = llm.invoke([
            SystemMessage(content=gen_system_msg),
            HumanMessage(content=gen_user_msg)
        ])
        
        # Log the test generation LLM call
        gen_tool_calls_info = []
        try:
            if hasattr(gen_response, 'tool_calls') and gen_response.tool_calls:
                gen_tool_calls_info = [{"id": tc.get('id'), "name": tc.get('name')} for tc in gen_response.tool_calls]
            
            log_experiment(
                agent_name="Judge",
                model_used=llm_no_tools.model_name if hasattr(llm_no_tools, 'model_name') else "unknown",
                action=ActionType.GENERATION,
                details={
                    "input_prompt": f"SYSTEM:\n{gen_system_msg}\n\nUSER:\n{gen_user_msg}",
                    "output_response": gen_response.content if hasattr(gen_response, 'content') else str(gen_response),
                    "tool_calls": gen_tool_calls_info,
                    "filename": base_name,
                    "action_type": "test_generation"
                },
                status="SUCCESS"
            )
        except Exception as e:
            print(f"⚠️ Logging failed in Judge (test generation): {e}")
        for tool_call in gen_response.tool_calls:
                args = tool_call['args']
                test_filename = args.get("filename")
                test_code = args.get("content")
                test_content += "FILE " + test_filename + "\n" + test_code + "\n"
                if test_filename and test_code:
                   write_file.invoke({
                   "filename": test_filename, 
                   "target_dir": state['project_root'], 
                   "content": test_code
               })
                
        
        
        

    raw_files = [f.strip() for f in filename.split("|")]

    test_files = []
    for f_path in raw_files:
      path_obj = Path(f_path)
    
      # 1. Get directory: "sandbox"
      # 2. Get filename: "inventory.py" -> prepend "test_" -> "test_inventory.py"
      # 3. Combine: "sandbox/test_inventory.py"
      test_name = path_obj.parent / f"test_{path_obj.name}"
    
      test_files.append(f"{target_dir}/{test_name}")
      
      raw_files = [f"{target_dir}/{f.strip()}" for f in filename.split("|")]
      # --- PHASE 2: RUN TESTS ---
    try:
        result = run_pytest(test_files, project_root=state['project_root'])
        passed = result["test_passed"]
        raw_output = result["stdout"] + result["stderr"]
    except Exception as e:
        passed = False
        raw_output = f"CRITICAL SYSTEM ERROR: {str(e)}"

    # --- PHASE 3: DECISION ---
    
    # A. SUCCESS CASE
    if passed:
        print("✅ Judge: Tests Passed.")
        pylint_res = run_pylint(raw_files)
        return Command(update={"pylint_score": pylint_res["score"], "test_errors": "Passed"}, goto=END)

    if iteration >= 7:
        print("🛑 Judge: Max retries reached.")
        pylint_res = run_pylint(raw_files)
        return Command(update={"pylint_score": pylint_res["score"],
                               "messages": [HumanMessage(content="Judge: Giving up after 7 failures.")]
                               },
                       goto=END)

    # --- PHASE 4: FORMALIZE FEEDBACK ---
    print("❌ Judge: Tests Failed. Formalizing feedback...")
    llm = get_llm(model_type="small")
    
    formalize_system_msg = FORMALIZE_SYSTEM_PROMPT
    formalize_user_msg = get_formalize_user_prompt(base_name, raw_output)
    
    analysis = llm.invoke([
        SystemMessage(content=formalize_system_msg),
        HumanMessage(content=formalize_user_msg)
    ])
    
    # Log the feedback formalization LLM call
    try:
        log_experiment(
            agent_name="Judge",
            model_used=llm.model_name if hasattr(llm, 'model_name') else "unknown",
            action=ActionType.DEBUG,
            details={
                "input_prompt": f"SYSTEM:\n{formalize_system_msg}\n\nUSER:\n{formalize_user_msg}",
                "output_response": analysis.content,
                "filename": base_name,
                "action_type": "feedback_formalization",
                "iteration": iteration
            },
            status="SUCCESS"
        )
    except Exception as e:
        print(f"⚠️ Logging failed in Judge (feedback formalization): {e}")
    
    return Command(
        update={
            "test_file": test_content,
            "test_errors": analysis.content,
            "iteration_count": iteration + 1,
            "messages": [HumanMessage(content=f"Judge: Tests failed.")]
        },
        goto="AUDITOR"
    )
