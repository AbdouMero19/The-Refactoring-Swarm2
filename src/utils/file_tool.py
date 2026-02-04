#ce fichier doit permettre aux agents de : lire des fichiers, ecrire des fichiers sans sortir de sandbox/ ou target_dir
import os #indispensable pour sandbox
from time import sleep
from langchain_core.tools import tool

def is_path_allowed(file_path: str, target_dir: str) -> bool:
    """
    Verifies that file_path is strictly inside target_dir (sandbox).
    
    Args:
        file_path: The file path to verify.
        target_dir: The target directory (sandbox) reference.
    
    Returns:
        bool: True if the file is strictly inside target_dir, False otherwise.
    """

    #chemains 
    real_file = os.path.realpath(file_path)
    real_dir = os.path.realpath(target_dir)

    # Vérifie que le fichier est strictement dans le dossier cible
    return real_file == real_dir or real_file.startswith(real_dir + os.sep)



def read_file(filename: str, target_dir: str) -> str:
    """
    Reads the content of a file in a secure manner.
    
    Args:
        filename: The filename to read (relative path to target_dir).
        target_dir: The target directory (sandbox) to restrict file access.
    
    Returns:
        str: The complete content of the file.
    
    Raises:
        PermissionError: If the file is not inside target_dir.
        FileNotFoundError: If the file does not exist.
    """
    sleep(2)
    full_path = os.path.join(target_dir, filename)

    if not is_path_allowed(full_path, target_dir):
        raise PermissionError("Lecture interdite hors sandbox !")

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Fichier introuvable : {full_path}")

    # ouvrir un fichier, lire son contenu, fermer lorsqu'on termine 
    with open(full_path, "r", encoding = "utf-8") as f:
        return f.read() #lire et renvoi tout le contenu du fichier 
    

@tool
def write_file(filename: str, target_dir: str, content: str) -> int:
    """
    Writes content to a file in a secure manner.
    
    Args:
        filename: The filename to write (relative path to target_dir).
        target_dir: The target directory (sandbox) to restrict file access.
        content: The content to write to the file.
    
    Returns:
        int: The number of characters written to the file.
    
    Raises:
        PermissionError: If the file is not inside target_dir.
    """
    sleep(2)  
    full_path = os.path.join(target_dir, filename)

    if not is_path_allowed(full_path, target_dir):
        raise PermissionError("Ecriture interdite hors sandbox !")

    # si le fichier n'existe pas, on le crée 
    os.makedirs(os.path.dirname(full_path), exist_ok = True)

    #ouvrir un fichier, ecrire sur le fichier, fermer lorsqu'on termine 
    with open(full_path, "w", encoding = "utf-8") as f:
        return f.write(content) 

