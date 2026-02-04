# Use Case 1: Test Generation
GEN_TEST_SYSTEM_PROMPT = "You are a QA Engineer specialized in Pytest (ActionType.GENERATION). Your task is to write comprehensive unit tests for the provided Python code to ensure full coverage and correctness."

def get_gen_test_user_prompt(base_name, code_content , signatures_map=None):
    return f"""
Write a Pytest test file for this code:

FILES (format : ./Path/FILE1 | ./Path/FILE2 | ...): {base_name}
--- SOURCE CODE ---
{code_content}

INSTRUCTIONS:
1. Import the module using: from FILEx import *
2. Write comprehensive unit tests.
3. Output ONLY valid Python code in a markdown block.
4. Don't do very complex tests; focus on core functionality.
5. only write logical tests that can run in isolation.
6. in case of multiple files (circular dependencies), you must generate a separate test file for each with names test_FILE1.py ... keeping the same folder as the original files ( no folder creation allowed) .
7. use the write_file function to write each test file separately.
8. don't be strict on floating point errors (use approx where necessary).
9.When patching classes in tests, always patch the location where the class is imported, not where it is defined.
10.When mocking a class that gets instantiated (e.g., db = Database()), ensure the test verifies the call to the mock class itself, or properly tracks the .return_value which represents the instance.
11.only Use the following methods and attributes that exist in the provided code. Do not invent new methods or attributes.:
{"".join(signatures_map) if signatures_map else ""}
"""
# Use Case 2: Formalizing Feedback
FORMALIZE_SYSTEM_PROMPT = "You are a Senior Debugger, Your mission is ActionType.DEBUG and validation. You must be strict: 100% test pass rate is required. If tests fail, explain exactly what broke to help the Fixer in the Self-Healing loop."

def get_formalize_user_prompt(base_name, raw_output): 
    return f"""
The unit tests failed for these files '{base_name}'.

--- RAW PYTEST OUTPUT --- {raw_output}
TASK:
1. Analyze the traceback.
2. Summarize the EXACT logic errors in plain English.
3. Ignore environment warnings. Focus on AssertionErrors and logic bugs.
4. Provide a clear bullet list of what needs to be fixed.
5. in case of multiple files (circular dependencies), you must separate the issues by file name.
6. in case of circular dependencies, keep the imports and do not remove them to a different module and do not implement them inside each other."""