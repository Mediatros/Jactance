"""Configuration centrale du prototype (chemins, constantes audio).

Force le mode hors ligne avant tout import HuggingFace : aucun téléchargement
ne doit jamais être tenté (contrainte airgap, CONSTITUTION P1/P3).
"""
import os

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT / "models" / "whisper-large-v3-turbo"

# Whisper attend du mono 16 kHz float32 ; capter dans ce format évite ffmpeg au runtime.
SAMPLE_RATE = 16000
CHANNELS = 1
LANGUAGE = "fr"
