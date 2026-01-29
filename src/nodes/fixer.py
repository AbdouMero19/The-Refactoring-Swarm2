from pathlib import Path
import re
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Command
from src.state.AgentState import AgentState
from src.models.gemini_models import get_llm
from src.utils.file_tool import write_file
from src.prompts.fixer_prompts import FIXER_SYSTEM_PROMPT, get_fixer_user_prompt

def fixer_node(state: AgentState) -> Command[Literal["JUDGE"]]:
    filename = state["filename"]
    current_code = state["code_content"]
    style_issues = state.get("style_issues", "No style issues reported.")
    test_errors = state.get("test_errors", "")
    
    if not test_errors: 
        test_errors = "None. Focus on style."

    print(f"🛠️ Fixer working on {Path(filename).name}...")
    
    llm = get_llm(model_type="pro") 
    response = llm.invoke([
        SystemMessage(content=FIXER_SYSTEM_PROMPT),
        HumanMessage(content=get_fixer_user_prompt(Path(filename).name, style_issues, test_errors, current_code))
    ])
    
    content = response.content
    code_match = re.search(r"```python(.*?)```", content, re.DOTALL)
    new_code = code_match.group(1).strip() if code_match else content

    write_file(Path(filename).name, Path(filename).parent, new_code)

    return Command(
        update={
            "code_content": new_code,
            "messages": [HumanMessage(content="Fixer: Applied changes to file.")]
        },
        goto="JUDGE"
    )