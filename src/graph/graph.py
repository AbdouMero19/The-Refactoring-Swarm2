from langgraph.graph import StateGraph, END , START 
from src.nodes.auditor import auditor_node
from src.nodes.fixer import fixer_node
from src.nodes.judge import judge_node
from src.state.AgentState import AgentState

def build_agent_graph() -> StateGraph[AgentState]:
    """
    Constructs the agent workflow graph using StateGraph.
    
    Nodes:
    1. JUDGE: Quality Assurance
    2. AUDITOR: Code Analysis
    3. FIXER: Code Refactoring
    
    The graph loops between these nodes until the END condition is met.
    """
    graph = StateGraph(AgentState)
    
    # Define nodes
    graph.add_node("JUDGE", judge_node)
    graph.add_node("AUDITOR", auditor_node)
    graph.add_node("FIXER", fixer_node)
    
    # Define edges (workflow)
    graph.add_edge(START, "AUDITOR")
    return graph

builder = build_agent_graph()
graph = builder.compile()