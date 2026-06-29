"""Orchestration du pipeline en application barre de menu.

Bascule : un appui sur Control + Command démarre l'enregistrement, un second
appui l'arrête et lance la transcription. Échap annule l'enregistrement en cours.
Le texte est nettoyé puis copié dans le presse-papiers (collage ⌘V manuel). Tout
est local, aucun accès réseau, aucune permission admin (combo et Échap détectés
par sondage d'état, voir src.hotkey.listener).
"""
from __future__ import annotations

import json
import sys
import threading
from pathlib import Path

import numpy as np
import rumps

from src.app import checks
from src.audio.recorder import Recorder, list_input_devices, resolve_device
from src.transcribe.engine import transcribe
from src.text.clean import clean
from src.clipboard.copy import copy
from src.hotkey.listener import HotkeyPoller
from src.config import SAMPLE_RATE, ROOT

IDLE = "🎤"      # repos / prêt
REC = "🎙️"       # enregistrement en cours
WORK = "🎤…"     # transcription en cours
OK = "🎤✅"       # transcription prête, copiée (persiste jusqu'au prochain enregistrement)
KO = "🎤❌"       # erreur ou aucune parole (persiste jusqu'au prochain enregistrement)
POLL_INTERVAL = 0.04  # 40 ms : latence imperceptible, charge CPU négligeable

# Préférence rangée à côté de l'app (jamais dans le bundle, qui est signé ad-hoc).
PREFS_PATH = ROOT / "jactance.prefs.json"
LAUNCH_AGENT_LABEL = "com.jactance.dictee"
LAUNCH_AGENT_PATH = Path.home() / "Library" / "LaunchAgents" / f"{LAUNCH_AGENT_LABEL}.plist"


def _load_prefs() -> dict:
    try:
        return json.loads(PREFS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_prefs(prefs: dict) -> None:
    """Écriture best-effort : sur support en lecture seule, on n'échoue pas."""
    try:
        PREFS_PATH.write_text(
            json.dumps(prefs, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception as e:
        print(f"[prefs] écriture impossible : {e}")


def _app_executable() -> str | None:
    """Binaire de la .app buildée, ou None hors packaging (mode ./run.sh)."""
    if getattr(sys, "frozen", False):
        return sys.executable
    return None


def _install_launch_agent() -> bool:
    exe = _app_executable()
    if not exe:
        return False
    plist = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
        '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
        '<plist version="1.0">\n'
        "<dict>\n"
        f"  <key>Label</key><string>{LAUNCH_AGENT_LABEL}</string>\n"
        "  <key>ProgramArguments</key>\n"
        f"  <array><string>{exe}</string></array>\n"
        "  <key>RunAtLoad</key><true/>\n"
        "</dict>\n"
        "</plist>\n"
    )
    try:
        LAUNCH_AGENT_PATH.parent.mkdir(parents=True, exist_ok=True)
        LAUNCH_AGENT_PATH.write_text(plist, encoding="utf-8")
        return True
    except Exception as e:
        print(f"[launchagent] installation impossible : {e}")
        return False


def _uninstall_launch_agent() -> bool:
    try:
        LAUNCH_AGENT_PATH.unlink(missing_ok=True)
        return True
    except Exception as e:
        print(f"[launchagent] retrait impossible : {e}")
        return False


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

        self._prefs = _load_prefs()
        self._mic_name = self._prefs.get("mic_name")
        self.menu = self._build_menu()

    def _build_menu(self) -> list:
        """Sous-menu micro, lancement auto (.app uniquement), dernière copie.

        La liste des micros est lue au démarrage ; pour prendre en compte un
        périphérique branché après coup, relancer l'application.
        """
        mic_parent = rumps.MenuItem("Micro")
        self._mic_items: list[tuple[rumps.MenuItem, int, str]] = []
        for index, name in list_input_devices():
            item = rumps.MenuItem(name, callback=self._select_mic)
            mic_parent.add(item)
            self._mic_items.append((item, index, name))
        self._refresh_mic_states()

        menu = [mic_parent]

        if _app_executable():
            launch_item = rumps.MenuItem("Lancer au démarrage", callback=self._toggle_launch)
            launch_item.state = 1 if LAUNCH_AGENT_PATH.exists() else 0
            menu.append(launch_item)

        menu.append(None)
        menu.append(self._last_item)
        return menu

    def _refresh_mic_states(self) -> None:
        """Coche le micro effectivement utilisé (préférence, sinon intégré)."""
        active = resolve_device(self._mic_name)
        for item, index, _name in self._mic_items:
            item.state = 1 if index == active else 0

    def _select_mic(self, sender) -> None:
        self._mic_name = sender.title
        self._prefs["mic_name"] = self._mic_name
        _save_prefs(self._prefs)
        self._refresh_mic_states()

    def _toggle_launch(self, sender) -> None:
        if sender.state:
            if _uninstall_launch_agent():
                sender.state = 0
                self._prefs["launch_at_login"] = False
                _save_prefs(self._prefs)
        elif _install_launch_agent():
            sender.state = 1
            self._prefs["launch_at_login"] = True
            _save_prefs(self._prefs)

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
            self.recorder.start(resolve_device(self._mic_name))
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
