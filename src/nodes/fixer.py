from pathlib import Path
import re
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Command
from src.state.AgentState import AgentState
from src.models.AI_models import get_llm
from src.utils.file_tool import write_file
from src.prompts.fixer_prompts import FIXER_SYSTEM_PROMPT, get_fixer_user_prompt
from src.utils.context import get_single_file_signature
from src.utils.logger import log_experiment, ActionType
import os
from time import sleep

def fixer_node(state: AgentState) -> Command[Literal["JUDGE"]]:
    sleep(4)  # To avoid rate limits
    filename = state["filename"]
    current_code = state["code_content"]
    style_issues = state.get("style_issues", "No style issues reported.")
    test_errors = state.get("test_errors", "None. Focus on style.")
    
    print(f"🛠️ Fixer working on {Path(filename).name}...")
    
    llm_no_tools = get_llm(model_type="large") 
    llm = llm_no_tools.bind_tools([write_file])
    
    system_msg = FIXER_SYSTEM_PROMPT
    user_msg = get_fixer_user_prompt(
        filename,
        style_issues,
        test_errors,
        current_code,
        context=state["signatures_map"].values(),
        test_file=state["test_file"] if "test_file" in state else None)
    
    response = llm.invoke([
        SystemMessage(content=system_msg),
        HumanMessage(content=user_msg)
    ])
    
    # Log the LLM call
    tool_calls_info = []
    try:
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_calls_info = [{"id": tc.get('id'), "name": tc.get('name')} for tc in response.tool_calls]
        
        log_experiment(
            agent_name="Fixer",
            model_used="mistral-large-latest",
            action=ActionType.FIX,
            details={
                "input_prompt": f"SYSTEM:\n{system_msg}\n\nUSER:\n{user_msg}",
                "output_response": response.content if hasattr(response, 'content') else str(response),
                "tool_calls": tool_calls_info,
                "filename": filename,
                "style_issues": style_issues[:200] if style_issues else "None"
            },
            status="SUCCESS"
        )
    except Exception as e:
        print(f"⚠️ Logging failed in Fixer: {e}")
    
    
    new_code = ""
    current_map = state["signatures_map"].copy() 
    for tool_call in response.tool_calls:
            args = tool_call['args']
            file_name = args.get("filename")
            content = args.get("content")
            if file_name and content:
               write_file.invoke({
                   "filename": file_name, 
                   "target_dir": state['project_root'], 
                   "content": content
               })
            new_code += "FILE " + file_name + "\n" + content + "\n"  # Update new_code with the content written
            current_map[file_name] = get_single_file_signature(file_name, content)
    
    # 🔄 2. Update the Dictionary (The Fast Part)
    # We grab the current map from state
    
    # We update ONLY the key for this file

    return Command(
        update={
            "signatures_map": current_map,
            "test_errors": "",
            "style_issues": "",
            "code_content": new_code,
            "messages": [HumanMessage(content="Fixer: Applied changes to file(s).")]
        },
        goto="JUDGE"
    )
                                                                                                                       