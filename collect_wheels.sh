#!/bin/bash
# Préparation du kit, à lancer sur une machine Apple Silicon CONNECTÉE (DEC-0006).
# Télécharge les wheels des dépendances dans vendor/wheels/ pour permettre une
# installation 100 % hors ligne sur la cible (install_offline.sh).
#
# Ne télécharge PAS le modèle : celui-ci est dissocié et ajouté manuellement.
set -euo pipefail
cd "$(dirname "$0")"

WHEELS="vendor/wheels"
PYTHON_BIN="${PYTHON_BIN:-python3}"

mkdir -p "$WHEELS"
"$PYTHON_BIN" -m pip download -r requirements.txt -d "$WHEELS"

echo
echo "Wheels collectées dans $WHEELS."
echo "Embarquez ce dossier dans le kit (le modèle reste à fournir séparément)."
