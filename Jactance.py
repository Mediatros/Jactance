"""Point d'entrée de l'application packagée (PyInstaller).

Identique au lancement `python -m src.app.main`, mais sous forme de script,
requis par PyInstaller pour l'analyse des imports.

`freeze_support()` doit être appelé avant tout import lourd : dans la .app
frozen, `sys.executable` est le binaire Jactance, donc chaque enfant
multiprocessing (spawn, défaut macOS) ré-exécute ce module. Sans cet appel en
tête, l'enfant relance l'application complète au lieu de son worker, ce qui
recharge le modèle en boucle (fork bomb, saturation mémoire).
"""
import multiprocessing

if __name__ == "__main__":
    multiprocessing.freeze_support()
    from src.app.main import main
    main()
