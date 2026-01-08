import os

from langchain_core.messages import SystemMessage, HumanMessage
from src.state.AgentState import AgentState
from src.models.gemini_models import get_llm
from src.utils.tools import write_file, run_pytest
from src.prompts.judge_prompts import get_judge_system_prompt , get_judge_user_prompt

def judge_node(state: AgentState):
    """
    The Judge Agent responsible for Quality Assurance.
    
    Strategy:
    1. Check if a test file (test_xxx.py) already exists.
    2. IF EXISTS: Reuse it (Save tokens/money).
    3. IF MISSING: Use the 'Pro' model to write a comprehensive test suite.
    4. Run the tests using Pytest.
    5. Update state with the test results.
    """
    print("\n--- ⚖️ JUDGE IS EVALUATING ---")

    # 1. Setup Data
    filename = state["filename"]
    code_content = state["code_content"]
    
    # Define the standard naming convention: sandbox/main.py -> sandbox/test_main.py
    # We split the path to handle folders correctly
    dir_name = os.path.dirname(filename)
    base_name = os.path.basename(filename)
    test_filename = os.path.join(dir_name, f"/tests/test_{base_name}")

    # 2. DECISION: Generate or Reuse?
    if os.path.exists(test_filename):
        print(f"✅ Existing tests found: {test_filename}. Reusing them.")
        # We don't need to invoke the LLM here. We just proceed to execution.
        generation_message = "Reused existing tests to verify logic."
    
    else:
        print(f"🆕 No tests found. Generating new test suite for: {filename}")
        
        # Initialize the "Smart" Model (Pro)
        llm = get_llm(model_type="pro").bind_tools([write_file])

        # Strict instructions for the Judge
        system_prompt = get_judge_system_prompt(test_filename, base_name)
        
        # SystemMessage(content=f"""
        # You are a QA Lead. Your job is to create a ROBUST test suite.
        
        # INSTRUCTIONS:
        # 1. Write a SINGLE test file named '{test_filename}'.
        # 2. Import the functions from the source file '{base_name}'.
        # 3. Create test functions (def test_...) for EVERY public function in the source code.
        # 4. Include 'happy paths' (valid inputs) and 'edge cases' (zeros, none, empty lists).
        # 5. DO NOT focus on style (pylint); focus purely on LOGIC correctness.
        # """)

        user_prompt = get_judge_user_prompt(code_content)
        
        # HumanMessage(content=f"""
        # Here is the code to test:
        # ```python
        # {code_content}
        # ```
        
        # Generate the test file now.
        # """)

        full_prompt = [system_prompt] + state["messages"] + [user_prompt]

        # Invoke the LLM
        response = llm.invoke(full_prompt)
        
        # EXECUTE THE TOOL (Critical Step)
        # The LLM returns a "tool_call" request. We must manually run it to save the file to disk.
        if response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call["name"] == "write_file":
                    # Extract arguments provided by the LLM
                    args = tool_call["args"]
                    # Actually write the file
                    write_file(args["filepath"], args["content"])
                    print(f"📝 Judge generated and saved: {args['filepath']}")
                    generation_message = "Generated new test suite."
        else:
            # Fallback if LLM refused to call the tool (rare with Pro)
            print("⚠️ Warning: Judge did not trigger write_file tool.")
            generation_message = "Judge failed to generate tests."

    # 3. EXECUTE PYTEST
    # Now that we are sure the file exists (old or new), we run it.
    print(f"🚀 Running Pytest on {test_filename}...")
    test_output = run_pytest(test_filename)
    
    # 4. Analyze Results
    # If the output contains "failed" or "error", we have work to do.
    # We update the state so the Fixer knows what to fix
    
    return {
        "test_errors": test_output,
        "messages": [HumanMessage(content=f"Test Execution Result: {test_output}")]
    }