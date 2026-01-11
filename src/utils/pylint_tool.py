# Un fichier pour l auditeur, pour detecter les erreurs 
import sys        # pour lancer pylint avec venv
import subprocess # pour executer des commandes externes (pylint)
import re         # necessaire pour obtinir un score numérique exact 
import os         # pour securiser path des fichiers
from typing import Dict # le format de sortie

# dict: contient le score, code retour, stdout, stderr, issues_count
def run_pylint(file_path: str) -> Dict:
    """
    Runs pylint on a single Python file and returns analysis results.
    
    Args:
        file_path: Path to the Python file to analyze
        
    Returns:
        Dict with keys: score, returncode, stdout, stderr, issues_count
    """
    # Verifie si le fichier existe
    if not os.path.isfile(file_path):
        return {
            "score": 0.0,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Erreur : le fichier '{file_path}' n'existe pas !",
            "issues_count": 0
        }

    # Verifie que c'est bien un fichier Python
    if not file_path.endswith('.py'):
        return {
            "score": 0.0,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Erreur : '{file_path}' n'est pas un fichier Python !",
            "issues_count": 0
        }
    
    try:
        # Execute pylint sur le fichier specifique
        result = subprocess.run(
            [sys.executable, "-m", "pylint", file_path],
            capture_output=True,
            text=True,
            timeout=30  # eviter les boucles infinies
        )

        stdout = result.stdout
        stderr = result.stderr
        returncode = result.returncode

    except subprocess.TimeoutExpired:
        return{
            "score": 0.0,
            "returncode": -2,
            "stdout": "",
            "stderr": "Erreur: pylint a depacé le délai !",
            "issues_count": 0
        }
    except Exception as e:
        return{
            "score": 0.0,
            "returncode": -3,
            "stdout": "",
            "stderr": f"Erreur: Erreur inattendue : {str(e)} !",
            "issues_count": 0
        }


    # extraire le score
    score = 0.0
    score_match = re.search(r"rated at (-?[0-9]+\.[0-9]+)", stdout)
    if score_match:
        try:
            score = float(score_match.group(1)) # convertir une chaine de caracteres en un nombre 
        except ValueError:
            score = 0.0


    # compter les lignes de probleme signalés par pylint
    lines = stdout.strip().split('\n') #.strip() : supprime les espaces et retours a la ligne , .split() : decoupe la chaine en une liste de lignes
    issues_count = 0
    for line in lines:
        line = line.strip()
        if line and not line.startswith("Your code") and ":" in line and any(code in line for code in ["C","W","E","F","R"]):
            # if line : si la ligne n est pas vide
            # ":" in line : toutes les vrais lignes de probleme dans pylint contiennent au moins un ":"
            # any(code in line for code in ["C","W","E","F","R"]) :verifie que la ligne contient un code de categorie pylint (convention, warning, error, fatal, refactor)

            issues_count += 1

    return {
        "score": score,
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
        "issues_count": issues_count

    }
