"""Vérifications de démarrage : micro, modèle, dépendances.

En cas de composant manquant, renvoie un message explicite. Ne tente jamais
de récupérer ou télécharger quoi que ce soit (contrainte airgap).
"""
from __future__ import annotations

from src.config import MODEL_DIR, SAMPLE_RATE


def check_model() -> str | None:
    if not MODEL_DIR.is_dir():
        return f"Modèle absent : {MODEL_DIR} (à déposer manuellement, aucun téléchargement)."
    missing = [name for name in ("config.json", "weights.safetensors") if not (MODEL_DIR / name).is_file()]
    if missing:
        return f"Modèle incomplet dans {MODEL_DIR} : fichier(s) manquant(s) {', '.join(missing)}."
    return None


def check_microphone() -> str | None:
    try:
        import sounddevice as sd
    except Exception as e:
        return f"Dépendance audio indisponible : {e}"
    inputs = [d for d in sd.query_devices() if d["max_input_channels"] > 0]
    if not inputs:
        return "Aucun micro détecté."
    return None


def check_dependencies() -> str | None:
    missing = []
    for mod in ("mlx_whisper", "numpy", "pyperclip", "rumps", "Quartz"):
        try:
            __import__(mod)
        except Exception:
            missing.append(mod)
    if missing:
        return "Dépendances manquantes : " + ", ".join(missing)
    return None


def run_all() -> list[str]:
    """Renvoie la liste des problèmes (vide si tout est OK)."""
    return [m for m in (check_dependencies(), check_model(), check_microphone()) if m]
