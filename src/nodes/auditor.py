# src/nodes/auditor.py

from src.state.AgentState import AgentState
from src.models.gemini_models import get_llm
from src.prompts.auditor_prompts import get_auditor_system_prompt , get_auditor_user_prompt

def auditor_node(state: AgentState) -> AgentState:
    """
    The Auditor scans the code for style violations (Pylint) and suspicious logical flaws.
    It does NOT fix the code; it only reports issues to the conversation history.
    """
    print("--- 🕵️ AUDITOR IS ANALYZING ---")
    
    # 1. Get the efficient 'Flash' model
    llm = get_llm(model_type="flash")
    
    # 2. Extract necessary data from state
    filename = state["filename"]
    code_content = state["code_content"]
    pylint_score = state.get("pylint_score", "N/A")
    
    # 3. Construct the System Prompt
    # We explicitly tell it to look for both Style (Pylint) and Logic.
    system_prompt = get_auditor_system_prompt
    
    # SystemMessage(content="""
    # You are a Senior Python Code Auditor. Your job is to analyze code for:
    # 1. Syntax Errors & Style Violations (PEP 8).
    # 2. Logical Bugs (off-by-one, variable scope, bad math, etc.).
    # 3. Missing Type Hints or Docstrings.
    
    # You must provide a clear, numbered list of issues.
    # DO NOT generate the full fixed code yet. Just analyze and report.
    # """)
    
    # 4. Construct the User Input
    # We include the current Pylint score to give the Auditor context on how bad it is.
    user_message = get_auditor_user_prompt(filename, pylint_score, code_content)

    # HumanMessage(content=f"""
    # Analyze the following Python file: '{filename}'
    # Current Pylint Score: {pylint_score}/10.0
    
    # CODE CONTENT:
    # ```python
    # {code_content}
    # ```
    
    # List the specific logical errors and style issues you find.
    # """)
    
    # 5. Invoke the LLM
    # We pass the full history so it knows if it's repeating itself,
    # but we prioritize the fresh analysis prompt.
    messages = [system_prompt] + state["messages"] + [user_message]
    response = llm.invoke(messages)
    
    # 6. Return the update
    # We simply append the Auditor's analysis to the message history.
    return {"messages": [response]}