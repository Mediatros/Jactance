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
# Par défaut le python3 d'Apple (3.9), seul compatible avec les wheels cp39 du
# kit. Sur une machine avec Homebrew, `python3` viserait une autre version et
# l'install échouerait ; on peut tout de même surcharger via PYTHON_BIN.
PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3}"
MODEL_DIR="assets/fr-pack"

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

# 2b. Garde-fou : le kit est en wheels cp39, le venv DOIT être en Python 3.9.
PYV="$("$VENV/bin/python" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || true)"
if [ "$PYV" != "3.9" ]; then
  echo "ERREUR : le venv $VENV est en Python ${PYV:-inconnu}, or le kit exige 3.9 (wheels cp39)." >&2
  echo "Supprimez-le et relancez avec le python3 d'Apple :" >&2
  echo "  rm -rf $VENV && PYTHON_BIN=/usr/bin/python3 ./install_offline.sh" >&2
  exit 1
fi

# 3. Installer les dépendances strictement hors ligne.
# --no-deps : on installe EXACTEMENT les wheels présentes dans le kit, sans
# laisser pip résoudre les métadonnées. mlx-whisper déclare torch en dépendance,
# mais torch est volontairement absent (inutile au runtime, DEC-0013) ; sans
# --no-deps, pip l'exigerait et l'installation échouerait hors ligne. vendor/wheels
# contient déjà l'ensemble résolu (torch exclu) produit par collect_wheels.sh.
"$VENV/bin/python" -m pip install --no-index --no-deps "$WHEELS"/*

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
