"""Copie du texte final dans le presse-papiers."""
import pyperclip


def copy(text: str) -> None:
    pyperclip.copy(text)
