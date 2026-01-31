AUDITOR_SYSTEM_PROMPT = """You are a Senior Code Auditor specialized in empirical software engineering. 
Your goal is to perform ActionType.ANALYSIS. You must produce a precise, actionable refactoring plan 
that identifies style violations, lack of documentation, and potential bugs based on static analysis 
(Pylint). Focus on making the code 'clean' as per research standards."""

def get_auditor_user_prompt(filename, score, raw_output):
    return f"""
FILE TO ANALYZE: {filename}
CURRENT PYLINT SCORE: {score}/10

RAW PYLINT OUTPUT:
{raw_output}

TASK:
1. Analyze the raw Pylint noise.
2. Produce a concise, bulleted refactoring plan for the Fixer Agent.
3. Explicitly list missing docstrings, naming convention violations, or complexity issues.
4. Do not provide code, only the diagnostic plan.
"""
