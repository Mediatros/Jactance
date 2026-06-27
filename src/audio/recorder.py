"""Capture micro en mémoire via sounddevice.

Enregistre en mono 16 kHz float32 (format attendu par Whisper, évite ffmpeg).
Modèle start/stop : démarrer au maintien de la touche, arrêter au relâchement,
récupérer le buffer concaténé.
"""
from __future__ import annotations

import numpy as np
import sounddevice as sd

from src.config import SAMPLE_RATE, CHANNELS


def list_input_devices() -> list[tuple[int, str]]:
    """(index, nom) de chaque périphérique d'entrée disponible."""
    result: list[tuple[int, str]] = []
    for index, dev in enumerate(sd.query_devices()):
        if dev.get("max_input_channels", 0) > 0:
            result.append((index, dev["name"]))
    return result


def _is_builtin(name: str) -> bool:
    low = name.lower()
    if "micro" not in low:
        return False
    return any(k in low for k in ("macbook", "built-in", "intégré", "integr"))


def find_builtin_device() -> int | None:
    """Index du micro intégré du Mac, sinon None."""
    for index, name in list_input_devices():
        if _is_builtin(name):
            return index
    return None


def resolve_device(preferred_name: str | None) -> int | None:
    """Micro à utiliser : préférence si branchée, sinon micro intégré, sinon
    None (laisse sounddevice prendre le périphérique par défaut du système)."""
    if preferred_name:
        for index, name in list_input_devices():
            if name == preferred_name:
                return index
    return find_builtin_device()


class Recorder:
    def __init__(self) -> None:
        self._frames: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None

    def _callback(self, indata, frames, time, status) -> None:
        if status:
            print(f"[audio] {status}")
        self._frames.append(indata.copy())

    def start(self, device: int | None = None) -> None:
        self._frames = []
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
            device=device,
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
