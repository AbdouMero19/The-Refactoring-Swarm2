import subprocess
import os
import re
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Command
from langgraph.graph import END
from src.state.AgentState import AgentState
from src.models.gemini_models import get_llm
from src.utils.file_tool import write_file
from src.utils.pylint_tool import run_pylint
from src.utils.agent_logger import log_judge_action

def judge_node(state: AgentState) -> Command[Literal["AUDITOR", END]]:
    """
    1. GENERATE TESTS: Writes a specific test file for the code.
    2. RUN TESTS: Executes pytest.
    3. ANALYZE (If Fail): Uses LLM to summarize exactly what went wrong.
    4. DECIDE: Pass -> End | Fail -> AUDITOR.
    """
    filename = state["filename"]
    code_content = state["code_content"]
    iteration = state.get("iteration_count", 0)
    
    # Setup paths
    base_name = os.path.basename(filename)
    dir_name = os.path.dirname(filename)
    test_filename = os.path.join(dir_name, f"test_{base_name}")

    print(f"⚖️ Judge: Evaluating {base_name}...")

    # --- PHASE 1: GENERATE TESTS ---
    llm = get_llm(model_type="pro")
    
    # We ask the LLM to write tests that are compatible with the file structure
    gen_prompt = f"""
    You are a QA Engineer. Write a Pytest test file for this code:
    
    FILE: {base_name}
    ```python
    {code_content}
    ```
    
    INSTRUCTIONS:
    1. Import the module using: `from {base_name.replace('.py', '')} import *`
    2. Write comprehensive unit tests.
    3. Output ONLY valid Python code in a markdown block.
    4. assume ONLY standard English vowels (a, e, i, o, u). Do NOT test accented characters.
    """
    
    response = llm.invoke([HumanMessage(content=gen_prompt)])
    
    # Extract code
    code_match = re.search(r"```python(.*?)```", response.content, re.DOTALL)
    test_code = code_match.group(1).strip() if code_match else response.content
    
    # Save test file
    with open(test_filename, "w" , encoding="utf-8") as f:
        f.write(test_code)

    # --- PHASE 2: RUN TESTS ---
    print(f"   -> Running generated tests...")

    # 1. Prepare the Environment
    # This is the magic trick. We add the sandbox root to Python's search path.
    env = os.environ.copy()
    project_root = state["project_root"]
    env["PYTHONPATH"] = f"{project_root}:{env.get('PYTHONPATH', '')}"

    try:
        # Run pytest and capture everything
        result = subprocess.run(
            ["pytest", test_filename],
            capture_output=True,
            text=True,
            timeout=10,
            env=env
        )
        passed = (result.returncode == 0)
        raw_output = result.stdout + result.stderr
        
    except Exception as e:
        passed = False
        raw_output = f"CRITICAL SYSTEM ERROR: {str(e)}"

    # --- PHASE 3: DECISION & FORMALIZATION ---
    
    # A. SUCCESS CASE
    if passed:
        print("✅ Judge: Tests Passed.")
        # Optional: Clean up test file
        # os.remove(test_filename)
        result = run_pylint(state["filename"])  # Re-run pylint to update score after fixes
        
        # Log successful test execution
        log_judge_action(
            filename=filename,
            test_filename=test_filename,
            test_output=raw_output[:500] + "..." if len(raw_output) > 500 else raw_output,
            generation_message="Tests passed",
            model_used="gemini-1.5-pro",
            status="SUCCESS"
        )
        
        return Command(
            update={
                "pylint_score": result["score"],
                "test_errors": "Passed",
                "messages": [HumanMessage(content="Judge: Code verified successfully.")]
            },
            goto=END
        )

    # B. MAX RETRIES CASE
    if iteration >= 3:
        print("🛑 Judge: Max retries reached.")
        result = run_pylint(state["filename"])  # Re-run pylint to update score after fixes
        
        # Log max retries failure
        log_judge_action(
            filename=filename,
            test_filename=test_filename,
            test_output=f"Max retries reached. Last output: {raw_output[:300]}",
            generation_message="Giving up after 3 iterations",
            model_used="N/A",
            status="FAILURE"
        )
        
        return Command(
            update={
                "pylint_score": result["score"],
                "messages": [HumanMessage(content="Judge: Giving up after 3 failures.")]
                },
            goto=END
        )

    # C. FAILURE CASE -> FORMALIZE THE ERROR
    print("❌ Judge: Tests Failed. Formalizing feedback...")
    
    # We use the LLM to translate "Computer Speak" (Traceback) to "Dev Speak" (Actionable Items)
    analysis_prompt = f"""
    You are a Senior Debugger.
    
    The unit tests failed for '{base_name}'.
    
    --- RAW PYTEST OUTPUT ---
    {raw_output}
    -------------------------
    
    TASK:
    1. Analyze the traceback.
    2. Summarize the EXACT logic errors in plain English.
    3. Ignore environment warnings. Focus on AssertionErrors and logic bugs.
    4. Provide a clear bullet list of what needs to be fixed.
    """
    
    analysis = llm.invoke([HumanMessage(content=analysis_prompt)])
    formalized_error = analysis.content
    
    # Log test failure with analysis
    log_judge_action(
        filename=filename,
        test_filename=test_filename,
        test_output=formalized_error,
        generation_message=f"Tests failed (iteration {iteration + 1})",
        model_used="gemini-1.5-pro",
        status="FAILURE"
    )
    
    return Command(
        update={
            # We overwrite the old errors with this new, clean analysis
            "test_errors": formalized_error,
            "iteration_count": iteration + 1,
            "messages": [HumanMessage(content=f"Judge: Tests failed. Feedback: {formalized_error}")]
        },
        goto="AUDITOR"
    )