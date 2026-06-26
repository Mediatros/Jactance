"""Chargement du modèle local et transcription Whisper MLX.

Le modèle est chargé exclusivement depuis un chemin local embarqué
(`path_or_hf_repo`). Aucun téléchargement n'est possible (mode offline forcé
dans config). En l'absence du modèle, lève une erreur explicite.
"""
import numpy as np
import mlx_whisper

from src.config import MODEL_DIR, LANGUAGE


def transcribe(audio: np.ndarray) -> str:
    """Transcrit un tableau audio mono 16 kHz float32 en texte français."""
    if not MODEL_DIR.is_dir():
        raise FileNotFoundError(
            f"Modèle introuvable : {MODEL_DIR}. "
            "Le modèle doit être embarqué localement, aucun téléchargement n'est effectué."
        )
    result = mlx_whisper.transcribe(
        audio,
        path_or_hf_repo=str(MODEL_DIR),
        language=LANGUAGE,
    )
    return result["text"].strip()
