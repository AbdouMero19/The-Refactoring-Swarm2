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
    response = llm.invoke([
        SystemMessage(content=FIXER_SYSTEM_PROMPT),
        HumanMessage(content=get_fixer_user_prompt(
            filename,
            style_issues,
            test_errors,
            current_code,
            context=state["signatures_map"].values(),
            test_file=state["test_file"] if "test_file" in state else None)
                     )
        ])
    
    # content = response.content
    # code_match = re.search(r"```python(.*?)```", content, re.DOTALL)
    # new_code = code_match.group(1).strip() if code_match else content

    # write_file(Path(filename).name, Path(filename).parent, new_code)
    new_code = ""
    current_map = state["signatures_map"].copy() 
    for tool_call in response.tool_calls:
            args = tool_call['args']
            file_name = args.get("filename")
            target_dir = args.get("target_dir")
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
                                                                                                                       