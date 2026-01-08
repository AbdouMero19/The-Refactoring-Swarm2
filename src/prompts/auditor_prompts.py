from langchain_core.messages import SystemMessage, HumanMessage

def get_auditor_system_prompt() -> SystemMessage:
    """
    System prompt for the Auditor Agent.
    
    The Auditor's role:
    - Analyze code for PEP 8 style violations
    - Identify logical bugs and errors
    - Create a clear, numbered list of issues with severity levels
    - DO NOT generate fixed code - only analysis
    """
    return SystemMessage(content="""Tu es un Auditeur Python Senior. Ton travail est d'analyser le code Python pour:
1. Erreurs de Syntaxe & Violations de Style (PEP 8)
2. Bugs Logiques (off-by-one, portée de variable, mauvaises mathématiques, etc.)
3. Absence de Type Hints ou Docstrings
4. Inefficacité algorithmique

Tu dois fournir une liste claire et numérotée des problèmes trouvés.
Pour chaque problème, inclus:
- Numéro du problème
- Sévérité (HAUTE / MOYENNE / BASSE)
- Emplacement exact (ligne, fonction)
- Description du problème
- Suggestion de correction

 - NE génère PAS le code corrigé complet. Seulement l'analyse et les recommandations.
 - Sois précis, technique et constructif.""")

def get_auditor_user_prompt(filename: str, pylint_score: str, code_content: str) -> HumanMessage:
    """
    User prompt for the Auditor Agent.
    
    Args:
        filename: Name of the file being analyzed
        pylint_score: Current Pylint score (format: X.XX/10.0)
        code_content: The full Python code to analyze
    
    Returns:
        HumanMessage with the analysis request
    """
    return HumanMessage(content=f"""Analyse le fichier Python suivant: '{filename}'
Score Pylint Actuel: {pylint_score}/10.0

CONTENU DU CODE:
```python
{code_content}
```""")





