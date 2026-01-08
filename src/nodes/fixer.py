from langchain_core.messages import SystemMessage, HumanMessage
from src.state.AgentState import AgentState
from src.models.gemini_models import get_llm
from src.utils.tools import write_file
from src.prompts.fixer_prompts import get_fixer_system_prompt , get_fixer_user_prompt

def fixer_node(state: AgentState):
    """
    The Fixer Agent applies changes to the code.
    It uses the 'write_file' tool to save changes to disk.
    """
    print("--- 🔧 FIXER IS WORKING ---")

    # 1. Setup
    # Use 'Flash' for speed and tool-calling reliability
    llm = get_llm(model_type="flash").bind_tools([write_file])
    
    filename = state["filename"]
    code_content = state["code_content"]
    test_errors = state.get("test_errors", "")

    # 2. Determine Focus (Style vs. Logic)
    # If there are test errors, PRIORITY = Logic.
    # Otherwise, PRIORITY = Style (Auditor's feedback).
    if test_errors and "failed" in test_errors.lower():
        focus_msg = f"""
        FOCUS: Fix the LOGIC errors reported by Pytest.
        Test Failures:
        {test_errors}
        """
    else:
        focus_msg = "FOCUS: Fix the Style/Syntax issues reported by the Auditor."

    # 3. System Prompt (The Rules)
    system_prompt = SystemMessage(content=f"""
    You are a Senior Python Developer. Your job is to fix the code in '{filename}'.
    
    CRITICAL RULES:
    1. ❌ STRICTLY FORBIDDEN: Changing function names, argument lists, or return types.
       - You must keep the API contract exactly as it is.
       - If arguments are badly named (e.g., 'x'), alias them INSIDE the function.
    2. ✅ ALLOWED: Changing internal logic, fixing bugs, adding type hints, adding docstrings.
    3. 🛠️ ACTION: You must call the 'write_file' tool with the full, fixed code.
    """)

    # 4. User Prompt (The Task)
    user_prompt = HumanMessage(content=f"""
    Current Code:
    ```python
    {code_content}
    ```
    
    {focus_msg}
    
    Output the fixed code using the 'write_file' tool now.
    """)

    # 5. Invoke LLM
    # We include the history so it sees the Auditor's complaints
    messages = [system_prompt] + state["messages"] + [user_prompt]
    response = llm.invoke(messages)

    # 6. Execute Tool & Update State
    tool_message = "Fixer failed to generate code."
    new_code = code_content # Fallback

    if response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call["name"] == "write_file":
                args = tool_call["args"]
                
                # A. Write to Disk
                write_file(args["filepath"], args["content"])
                
                # B. Update Memory (Critical!)
                # We update 'code_content' in the state so the next agent 
                # reads the new version immediately without disk I/O.
                new_code = args["content"]
                
                tool_message = f"Fixer applied changes to {args['filepath']}."
                print(f"✅ Fixed code saved to {args['filepath']}")

    return {
        "code_content": new_code, # Update the state with the new code
        "messages": [HumanMessage(content=tool_message)]
    }