#!/bin/bash
# Collecte les wheels de BUILD (PyInstaller) pour fabriquer Jactance.app
# directement sur la cible, hors ligne (DEC-0014). À lancer sur une machine
# Apple Silicon CONNECTÉE, avec le MÊME Python que la cible (le python3 d'Apple,
# 3.9) afin d'obtenir des wheels compatibles : PYTHON_BIN=/usr/bin/python3.
#
# Ne télécharge ni les dépendances runtime (collect_wheels.sh) ni le modèle.
set -euo pipefail
cd "$(dirname "$0")"

WHEELS="vendor/build-wheels"
# Défaut : python3 d'Apple (3.9), même Python que la cible. Surchargeable.
PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3}"

mkdir -p "$WHEELS"
"$PYTHON_BIN" -m pip download -r requirements-build.txt -d "$WHEELS"

echo
echo "Wheels de build collectées dans $WHEELS."
echo "Embarquez ce dossier dans le kit ; le build se fait sur la cible : ./build_app.sh"
