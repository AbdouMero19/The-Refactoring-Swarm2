from typing import TypedDict, Annotated, List, Union
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Represents the memory of the agent workflow.
    This state is RESET for every new file processed in main.py.
    """
    
    # --- CONVERSATION HISTORY ---
    # We use 'add_messages' so that when a node returns {"messages": [new_msg]},
    # it APPENDS to this list rather than deleting the old history.
    messages: Annotated[List[AnyMessage], add_messages]

    # --- FILE CONTEXT ---
    filename: str       # e.g., "sandbox/bad_code.py"
    code_content: str   # The actual text of the code (synced with disk)

    # --- METRICS & FEEDBACK ---
    pylint_score: float # e.g., 8.5
    test_errors: str    # Output from Pytest. Empty if all tests pass.

    # --- SAFETY ---
    iteration_count: int # Tracks how many times we've looped (to stop infinite loops)