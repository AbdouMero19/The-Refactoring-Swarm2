# Use Case 1: Test Generation
GEN_TEST_SYSTEM_PROMPT = "You are a QA Engineer specialized in Pytest."

def get_gen_test_user_prompt(base_name, code_content):
    return f"""
Write a Pytest test file for this code:

FILE: {base_name}
```python
{code_content}
INSTRUCTIONS:
Import the module using: from {base_name.replace('.py', '')} import *
Write comprehensive unit tests.
Output ONLY valid Python code in a markdown block.
assume ONLY standard English vowels (a, e, i, o, u). Do NOT test accented characters. """

# Use Case 2: Formalizing Feedback
FORMALIZE_SYSTEM_PROMPT = "You are a Senior Debugger."

def get_formalize_user_prompt(base_name, raw_output): return f""" The unit tests failed for '{base_name}'.

--- RAW PYTEST OUTPUT --- {raw_output}
TASK:
Analyze the traceback.
Summarize the EXACT logic errors in plain English.
Ignore environment warnings. Focus on AssertionErrors and logic bugs.
Provide a clear bullet list of what needs to be fixed. """