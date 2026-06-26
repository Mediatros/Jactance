"""Nettoyage minimal du texte transcrit."""
import re


def clean(text: str) -> str:
    """Normalise les espaces et retire les espaces de bord."""
    return re.sub(r"\s+", " ", text).strip()
