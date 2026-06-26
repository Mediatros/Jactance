"""Détection clavier par sondage d'état (zéro permission).

Lit l'état clavier via CGEventSourceFlagsState (modificateurs) et
CGEventSourceKeyState (touche précise) : simples requêtes d'état, sans event
tap, donc NI Accessibilité NI Surveillance de la saisie, aucun droit admin sur
le poste cible airgap.

Mode bascule : un front montant du combo (Control + Command) bascule
enregistrement marche/arrêt. Échap déclenche une annulation. Le sondage est
piloté par l'appelant (rumps.Timer) via `poll()`.
"""
from Quartz import (
    CGEventSourceFlagsState,
    CGEventSourceKeyState,
    kCGEventSourceStateCombinedSessionState,
    kCGEventFlagMaskControl,
    kCGEventFlagMaskCommand,
)

CHORD_MASK = kCGEventFlagMaskControl | kCGEventFlagMaskCommand
KEYCODE_ESCAPE = 53


def chord_held(mask: int = CHORD_MASK) -> bool:
    """Vrai si tous les modificateurs du masque sont actuellement tenus."""
    flags = CGEventSourceFlagsState(kCGEventSourceStateCombinedSessionState)
    return (flags & mask) == mask


def key_down(keycode: int) -> bool:
    """Vrai si la touche de ce keycode est actuellement enfoncée."""
    return bool(CGEventSourceKeyState(kCGEventSourceStateCombinedSessionState, keycode))


class HotkeyPoller:
    def __init__(self, on_toggle, on_cancel, mask: int = CHORD_MASK) -> None:
        self._mask = mask
        self._on_toggle = on_toggle
        self._on_cancel = on_cancel
        self._chord = False
        self._esc = False

    def poll(self) -> None:
        """À appeler périodiquement ; émet on_toggle / on_cancel sur fronts montants."""
        chord = chord_held(self._mask)
        if chord and not self._chord:
            self._on_toggle()
        self._chord = chord

        esc = key_down(KEYCODE_ESCAPE)
        if esc and not self._esc:
            self._on_cancel()
        self._esc = esc
