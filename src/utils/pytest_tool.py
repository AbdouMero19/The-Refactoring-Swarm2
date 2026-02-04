#PS: take care of the file name, pytest_tool was not accepted as a file name since there is *test* in gitignore

from datetime import time
import subprocess
import os
import sys
from typing import Dict
from time import sleep


def run_pytest(file_list: list, project_root: str = None) -> Dict:
    sleep(2)
    # 1. Vérification du chemin
    for file in file_list:
      if not os.path.exists(file):
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": f"Erreur : le chemin '{file}' n'existe pas.",
            "test_passed": False,
            "error_summary": "Chemin introuvable."
        }

    # 2. Préparation de l'environnement
    env = os.environ.copy()
    if project_root is None:
        project_root = os.path.dirname(os.path.abspath(file_list[0]))
    
    current_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{project_root}{os.pathsep}{current_pythonpath}"

    # 3. Exécution de pytest
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", *file_list, "-v"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        stdout = result.stdout
        stderr = result.stderr
        returncode = result.returncode

    except subprocess.TimeoutExpired:
        return {
            "returncode": -2,
            "stdout": "",
            "stderr": "Erreur : pytest a dépassé le délai de 30 secondes.",
            "test_passed": False,
            "error_summary": "Timeout lors de l'exécution des tests."
        }
    except Exception as e:
        return {
            "returncode": -3,
            "stdout": "",
            "stderr": f"Erreur inattendue : {str(e)}",
            "test_passed": False,
            "error_summary": f"Exception système : {str(e)}"
        }

    # 4. Analyse du résultat
    test_passed = (returncode == 0)
    error_summary = ""

    if not test_passed:
        # Cas 1 : Section FAILURES présente dans stdout
        if "===== FAILURES =====" in stdout:
            lines = stdout.split('\n')
            in_failures = False
            failure_lines = []
            for line in lines:
                if "===== FAILURES =====" in line:
                    in_failures = True
                    continue
                if in_failures and ("=====" in line or "=== short test summary info ===" in line):
                    break
                if in_failures and line.strip():
                    failure_lines.append(line)
            error_summary = "\n".join(failure_lines)

        # Cas 2 : Si aucun FAILURES, utiliser stderr s'il contient des erreurs
        if not error_summary and stderr.strip():
            error_summary = stderr.strip()

        # Cas 3 : Sinon, utiliser les dernières lignes de stdout
        if not error_summary:
            lines = stdout.strip().split('\n')
            error_summary = "\n".join(lines[-10:]) if lines else "Erreur inconnue."

    # 5. Retour du résultat structuré
    return {
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
        "test_passed": test_passed,
        "error_summary": error_summary
    }