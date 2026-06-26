#!/bin/bash
# Installe l'environnement de la dictée locale, 100 % hors ligne.
#
# Ce script N'INSTALLE PAS le modèle Whisper : il est dissocié de l'installation
# et doit être ajouté manuellement dans models/ (voir le message de fin).
# Aucune connexion réseau n'est utilisée : les dépendances sont installées depuis
# des wheels locales préparées au préalable (collect_wheels.sh, contrainte airgap).
set -euo pipefail
cd "$(dirname "$0")"

VENV=".venv"
WHEELS="vendor/wheels"
PYTHON_BIN="${PYTHON_BIN:-python3}"
MODEL_DIR="models/whisper-large-v3-turbo"

# 1. Wheels embarquées requises (aucun téléchargement réseau n'est autorisé).
if [ ! -d "$WHEELS" ] || [ -z "$(ls -A "$WHEELS" 2>/dev/null)" ]; then
  echo "ERREUR : dossier de wheels absent ou vide : $WHEELS" >&2
  echo "Préparez le kit sur une machine connectée : ./collect_wheels.sh" >&2
  exit 1
fi

# 2. Créer le venv s'il n'existe pas (ne pas écraser un venv existant).
if [ ! -d "$VENV" ]; then
  "$PYTHON_BIN" -m venv "$VENV"
fi

# 3. Installer les dépendances strictement hors ligne.
"$VENV/bin/python" -m pip install --no-index --find-links "$WHEELS" -r requirements.txt

# 4. Vérifier le modèle SANS l'installer ni le télécharger.
echo
echo "Environnement installé."
if [ -f "$MODEL_DIR/config.json" ] && [ -f "$MODEL_DIR/weights.safetensors" ]; then
  echo "Modèle détecté : $MODEL_DIR"
else
  echo "ATTENTION : le modèle n'est PAS inclus dans cette installation."
  echo "Déposez le dossier du modèle dans : $MODEL_DIR"
  echo "(il doit contenir config.json ET weights.safetensors)"
fi
echo "Lancement : ./run.sh"
