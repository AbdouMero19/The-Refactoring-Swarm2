import os
import sys

# Ajoute le dossier 'src' au chemin Python pour pouvoir importer
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Importe ta fonction
from utils.pylint_tool import run_pylint

def test_pylint_normal():
    """Test sur du code buggé : doit retourner un score bas et des issues."""
    print("🧪 Test normal (code buggé)...")
    result = run_pylint("./sandbox/test_pylint")
    
    # Vérifications critiques
    assert isinstance(result, dict), "❌ Résultat n'est pas un dictionnaire"
    assert "score" in result, "❌ Clé 'score' manquante"
    assert "issues_count" in result, "❌ Clé 'issues_count' manquante"
    assert 0.0 <= result["score"] <= 10.0, f"❌ Score invalide : {result['score']}"
    assert result["issues_count"] > 0, "❌ Aucun problème détecté dans du code buggé !"
    assert result["returncode"] != 0, "❌ pylint n'a pas signalé d'erreurs"
    
    print(f"✅ Score : {result['score']:.2f}/10")
    print(f"✅ Problèmes détectés : {result['issues_count']}")
    print(f"✅ Return code : {result['returncode']}")

    print("=== STDOUT DE PYLINT ===")
    print(result["stdout"])
    print("=== STDERR DE PYLINT ===")
    print(result["stderr"])

    return True

def test_pylint_dossier_inexistant():
    """Test sur un dossier qui n'existe pas : ne doit pas planter."""
    print("\n🧪 Test dossier inexistant...")
    result = run_pylint("./sandbox/DOSSIER_INEXISTANT")
    
    assert result["score"] == 0.0, "❌ Score devrait être 0.0"
    assert result["issues_count"] == 0, "❌ issues_count devrait être 0"
    assert "n'existe pas" in result["stderr"], "❌ Message d'erreur incorrect"
    
    print("✅ Gestion du dossier inexistant : OK")
    return True

def test_pylint_dossier_vide():
    """Test sur un dossier vide : ne doit pas planter."""
    print("\n🧪 Test dossier vide...")
    os.makedirs("./sandbox/test_vide", exist_ok=True)
    result = run_pylint("./sandbox/test_vide")
    
    # pylint retourne généralement un score de 0.0 ou 10.0 sur dossier vide, mais ne doit pas crasher
    assert isinstance(result["score"], (int, float)), "❌ Score n'est pas un nombre"
    print(f"✅ Dossier vide géré (score : {result['score']})")
    return True

if __name__ == "__main__":
    try:
        test_pylint_normal()
        test_pylint_dossier_inexistant()
        test_pylint_dossier_vide()
        print("\n🎉 TOUT EST OK ! Ta fonction run_pylint est robuste et fiable.")
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        sys.exit(1)