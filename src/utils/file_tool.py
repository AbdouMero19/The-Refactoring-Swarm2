#ce fichier doit permettre aux agents de : lire des fichiers, ecrire des fichiers sans sortir de sandbox/ ou target_dir
import os #indispensable pour sandbox

def is_path_allowed(file_path: str, target_dir: str) -> bool:
    """
    Vérifie que file_path est bien à l'interieur de target_dir (sandbox)
    """

    #chemains 
    real_file = os.path.realpath(file_path)
    real_dir = os.path.realpath(target_dir)

    # Vérifie que le fichier est strictement dans le dossier cible
    return real_file == real_dir or real_file.startswith(real_dir + os.sep)



# fonction pour lire un fichier en sécurité 
def read_file(filename: str, target_dir: str) -> str:
    """
    Lit le contenu d'un fichier de maniere securisée
    """
    full_path = os.path.join(target_dir, filename)

    if not is_path_allowed(full_path, target_dir):
        raise PermissionError("Lecture interdite hors sandbox !")

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Fichier introuvable : {full_path}")

    # ouvrir un fichier, lire son contenu, fermer lorsqu'on termine 
    with open(full_path, "r", encoding = "utf-8") as f:
        return f.read() #lire et renvoi tout le contenu du fichier 
    

#fonction pour ecrire dans un fichier en securité
def write_file(filename: str, target_dir: str, content: str) -> int:
    full_path = os.path.join(target_dir, filename)

    if not is_path_allowed(full_path, target_dir):
        raise PermissionError("Ecriture interdite hors sandbox !")

    # si le fichier n'existe pas, on le crée 
    os.makedirs(os.path.dirname(full_path), exist_ok = True)

    #ouvrir un fichier, ecrire sur le fichier, fermer lorsqu'on termine 
    with open(full_path, "w", encoding = "utf-8") as f:
        return f.write(content) 