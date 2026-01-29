FIXER_SYSTEM_PROMPT = """You are a Senior Python Refactoring Agent.
Your goal is ActionType.FIX. You rewrite code to fix logic failures and improve quality."""

def get_fixer_user_prompt(filename, style_issues, test_errors, current_code):
    return f"""
FILE: {filename}

--- STYLE ISSUES ---
{style_issues}

--- LOGIC FAILURES ---
{test_errors if test_errors else "None. Focus on quality."}

--- SOURCE CODE ---
```python
{current_code}
INSTRUCTIONS:
Fix logic failures first to ensure the code is functional.
Adhere to style feedback and add missing documentation.
RETURN ONLY THE FULL PYTHON CODE inside markdown blocks. """