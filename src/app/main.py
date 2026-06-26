"""Orchestration du pipeline en application barre de menu.

Bascule : un appui sur Control + Command démarre l'enregistrement, un second
appui l'arrête et lance la transcription. Échap annule l'enregistrement en cours.
Le texte est nettoyé puis copié dans le presse-papiers (collage ⌘V manuel). Tout
est local, aucun accès réseau, aucune permission admin (combo et Échap détectés
par sondage d'état, voir src.hotkey.listener).
"""
import threading

import numpy as np
import rumps

from src.app import checks
from src.audio.recorder import Recorder
from src.transcribe.engine import transcribe
from src.text.clean import clean
from src.clipboard.copy import copy
from src.hotkey.listener import HotkeyPoller
from src.config import SAMPLE_RATE

IDLE = "🎤"      # repos / prêt
REC = "🎙️"       # enregistrement en cours
WORK = "🎤…"     # transcription en cours
OK = "🎤✅"       # transcription prête, copiée (persiste jusqu'au prochain enregistrement)
KO = "🎤❌"       # erreur ou aucune parole (persiste jusqu'au prochain enregistrement)
POLL_INTERVAL = 0.04  # 40 ms : latence imperceptible, charge CPU négligeable


class DicteeApp(rumps.App):
    def __init__(self) -> None:
        super().__init__("Dictée", title=IDLE, quit_button="Quitter")
        self.recorder = Recorder()
        self.hotkey = HotkeyPoller(on_toggle=self._on_toggle, on_cancel=self._on_cancel)
        self._busy = False
        self._recording = False
        self._timer = rumps.Timer(self._poll, POLL_INTERVAL)
        self._last_text = ""
        self._last_item = rumps.MenuItem("Aucune transcription", callback=None)
        self.menu = [self._last_item]

    def start(self) -> None:
        problems = checks.run_all()
        if problems:
            rumps.alert("Dictée — composant manquant", "\n".join(problems))
            return
        threading.Thread(target=self._warmup, daemon=True).start()
        self._timer.start()
        self.run()

    def _poll(self, _timer) -> None:
        self.hotkey.poll()

    def _copy_last(self, _item) -> None:
        if self._last_text:
            copy(self._last_text)

    def _warmup(self) -> None:
        """Précharge le modèle sur un court silence pour accélérer le 1er usage."""
        try:
            transcribe(np.zeros(SAMPLE_RATE // 2, dtype="float32"))
        except Exception as e:
            print(f"[warmup] {e}")

    def _on_toggle(self) -> None:
        if self._busy:
            return
        if not self._recording:
            self._recording = True
            self.title = REC
            self.recorder.start()
        else:
            self._recording = False
            audio = self.recorder.stop()
            self.title = WORK
            threading.Thread(target=self._process, args=(audio,), daemon=True).start()

    def _on_cancel(self) -> None:
        """Échap : abandonne l'enregistrement en cours, sans transcrire."""
        if self._recording and not self._busy:
            self._recording = False
            self.recorder.stop()
            self.title = IDLE
            print("[annulé]")

    def _process(self, audio: np.ndarray) -> None:
        self._busy = True
        try:
            text = clean(transcribe(audio)) if audio.size else ""
            if text:
                copy(text)
                self._last_text = text
                preview = text if len(text) <= 50 else text[:50] + "…"
                self._last_item.title = f"Copier : {preview}"
                self._last_item.set_callback(self._copy_last)
                self.title = OK
                print(f"[copié] {text}")
            else:
                self.title = KO
                print("[vide] aucune parole détectée")
        except Exception as e:
            self.title = KO
            print(f"[erreur] {e}")
        finally:
            self._busy = False


def main() -> None:
    DicteeApp().start()


if __name__ == "__main__":
    main()
