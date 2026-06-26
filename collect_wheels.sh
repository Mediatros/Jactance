#!/bin/bash
# Préparation du kit, à lancer sur une machine Apple Silicon CONNECTÉE (DEC-0006).
# Télécharge les wheels des dépendances dans vendor/wheels/ pour permettre une
# installation 100 % hors ligne sur la cible (install_offline.sh).
#
# Ne télécharge PAS le modèle : celui-ci est dissocié et ajouté manuellement.
set -euo pipefail
cd "$(dirname "$0")"

WHEELS="vendor/wheels"
# Défaut : python3 d'Apple (3.9), pour produire des wheels cp39 compatibles avec
# la cible. Surchargeable via PYTHON_BIN si la cible utilise un autre Python.
PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3}"

mkdir -p "$WHEELS"
"$PYTHON_BIN" -m pip download -r requirements.txt -d "$WHEELS"

# torch (et ses dépendances exclusives sympy/networkx/mpmath) est tiré par
# mlx-whisper mais JAMAIS utilisé au runtime : transcribe() n'active pas
# word_timestamps, seul cas où Whisper appelle torch. Vérifié empiriquement.
# On le retire du kit (gain ~340 Mo). L'install se fait ensuite en --no-deps.
# Voir DEC-0013.
for pkg in torch sympy networkx mpmath; do
  find "$WHEELS" -maxdepth 1 -iname "${pkg}-*" -delete
done

echo
echo "Wheels collectées dans $WHEELS (torch exclu, DEC-0013)."
echo "Embarquez ce dossier dans le kit (le modèle reste à fournir séparément)."
