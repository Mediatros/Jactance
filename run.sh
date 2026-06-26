#!/bin/bash
# Lance l'application de dictée (prototype non packagé).
# Hors ligne : aucun accès réseau, modèle chargé localement.
set -e
cd "$(dirname "$0")"
exec .venv/bin/python -m src.app.main
