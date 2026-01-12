from pathlib import Path
import re
from typing import Literal
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from src.state.AgentState import AgentState
from src.models.gemini_models import get_llm
from src.utils.file_tool import write_file
from src.utils.agent_logger import log_fixer_action

def fixer_node(state: AgentState) -> Command[Literal["JUDGE"]]:
    """
    1. Reads code_content directly from STATE.
    2. Invokes LLM to fix Style + Logic issues.
    3. Writes the fixed code to DISK.
    4. Updates 'code_content' in STATE.
    5. Routes to 'JUDGE'.
    """
    filename = state["filename"]
    # ✅ CORRECTED: Read from state, not disk
    current_code = state["code_content"]

    # --- 1. PREPARE INPUTS ---
    style_issues = state.get("style_issues", "No style issues reported.")
    test_errors = state.get("test_errors", "")
    
    if not test_errors: 
        test_errors = "None. Focus on style."

    print(f"🛠️ Fixer working on {Path(filename).name}...")
    
    # --- 2. UNIFIED PROMPT ---
    prompt = f"""
    You are a Senior Python Refactoring Agent.
    
    FILE: {Path(filename).name}
    
    --- 1. STYLE ISSUES (Pylint) ---
    {style_issues}
    
    --- 2. LOGIC FAILURES (Pytest) ---
    {test_errors}
    
    --- 3. SOURCE CODE ---
    ```python
    {current_code}
    ```
    
    INSTRUCTIONS:
    1. Rewrite the code to fix the Logic Failures first.
    2. Then, ensure the code adheres to the Style feedback.
    3. RETURN ONLY THE FULL PYTHON CODE inside markdown code blocks.
    4. Do not add explanations outside the code block.
    """

    # --- 3. INVOKE LLM ---
    llm = get_llm(model_type="pro") 
    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content

    # --- 4. EXTRACT CODE ---
    code_match = re.search(r"```python(.*?)```", content, re.DOTALL)
    
    if code_match:
        new_code = code_match.group(1).strip()
    else:
        # Fallback if LLM forgets the backticks
        print("⚠️ Warning: Could not parse markdown. Assuming raw output is code.")
        new_code = content

    # --- 5. WRITE TO DISK (Sync) ---
    # We must save to disk so the JUDGE (subprocess) can run the file later.
    write_file(Path(filename).name, Path(filename).parent, new_code)

    # with open(filename, "w") as f:
    #     f.write(new_code)
    # print(f"💾 Fixer saved changes to {filename}.")
    
    # Log the fix action
    log_fixer_action(
        filename=filename,
        input_prompt=prompt[:500] + "..." if len(prompt) > 500 else prompt,  # Truncate for readability
        output_response=f"Applied fixes to {Path(filename).name}",
        changes_applied=True,
        status="SUCCESS"
    )

    # --- 6. RETURN COMMAND ---
    return Command(
        # Update the state with the new code
        update={
            "code_content": new_code,  # Update the in-memory version
            "messages": [HumanMessage(content="Fixer: Applied changes to file.")]
        },
        # Always verify work with the JUDGE
        goto="JUDGE"
    )