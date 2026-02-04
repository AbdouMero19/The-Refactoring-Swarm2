FIXER_SYSTEM_PROMPT = """You are a Senior Python Refactoring Agent.
Your goal is ActionType.FIX. You rewrite code to fix logic failures and improve quality. Only write python code and don't include any explanations."""

def get_fixer_user_prompt(filename, style_issues, test_errors, current_code,context, test_file=""):
    return f"""
FILES (format : ./Path/FILE1 | ./Path/FILE2 | ...): {filename}

--- STYLE ISSUES ---
{style_issues}

--- LOGIC FAILURES ---
{test_errors if test_errors else "None. Focus on quality."}

--- SOURCE CODE ---
{current_code}

--- PROJECT SIGNATURES ---
Use the following map to verify methods and attributes in other files
{"".join(context)}

### 📜 THE UNIT TEST FILE (The Source of Truth)
Below is the content of the test file that your code MUST pass. 
Pay close attention to:
- Expected method names and arguments.
- The EXACT strings in error messages (e.g., ValueError("...")).
- Expected return types (Dictionaries vs. Objects).

{test_file if test_file else "No test file provided."}

--- INSTRUCTIONS ---
1. Fix logic failures first to ensure the code is functional.
2. Adhere to style feedback and add missing documentation.
3. RETURN ONLY THE FULL PYTHON CODE inside markdown blocks.
4. Cross-reference the signatures_map for every class you instantiate. If a field is missing, you must fix the class definition first.
6. do not reimplement functionalities and classes already covered by existing methods in other files.
7. if you have more than one file to fix (case of circular dependencies), you must generate two separate files and do not merge them together.
8. use the write_file function to write each file separately."""