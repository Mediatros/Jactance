"""Capture micro en mémoire via sounddevice.

Enregistre en mono 16 kHz float32 (format attendu par Whisper, évite ffmpeg).
Modèle start/stop : démarrer au maintien de la touche, arrêter au relâchement,
récupérer le buffer concaténé.
"""
from __future__ import annotations

import numpy as np
import sounddevice as sd

from src.config import SAMPLE_RATE, CHANNELS


class Recorder:
    def __init__(self) -> None:
        self._frames: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None

    def _callback(self, indata, frames, time, status) -> None:
        if status:
            print(f"[audio] {status}")
        self._frames.append(indata.copy())

    def start(self) -> None:
        self._frames = []
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()

    def stop(self) -> np.ndarray:
        """Arrête la capture et renvoie l'audio mono float32 (vide si rien)."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if not self._frames:
            return np.zeros(0, dtype="float32")
        return np.concatenate(self._frames, axis=0).reshape(-1)
