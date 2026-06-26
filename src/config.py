"""Configuration centrale du prototype (chemins, constantes audio).

Force le mode hors ligne avant tout import HuggingFace : aucun téléchargement
ne doit jamais être tenté (contrainte airgap, CONSTITUTION P1/P3).
"""
import os

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    # Application packagée (.app) : le pack est cherché dans le dossier qui
    # contient le bundle (kit relogeable : Jactance.app + assets/ côte à côte).
    # sys.executable = .../Jactance.app/Contents/MacOS/Jactance -> parents[3].
    ROOT = Path(sys.executable).resolve().parents[3]
else:
    ROOT = Path(__file__).resolve().parent.parent

MODEL_DIR = ROOT / "assets" / "fr-pack"

# Whisper attend du mono 16 kHz float32 ; capter dans ce format évite ffmpeg au runtime.
SAMPLE_RATE = 16000
CHANNELS = 1
LANGUAGE = "fr"
