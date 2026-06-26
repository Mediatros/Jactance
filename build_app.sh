#!/bin/bash
# Fabrique Jactance.app LOCALEMENT sur la cible, hors ligne (DEC-0014).
#
# Pourquoi builder sur place : une app construite localement ne porte jamais le
# tag com.apple.quarantine (celui-ci n'est posé que sur ce qui est téléchargé).
# Gatekeeper ne bloque alors pas son lancement, sans admin ni notarisation.
#
# Prérequis : l'environnement runtime doit déjà être installé (./install_offline.sh),
# car PyInstaller embarque ce qu'il trouve dans ce venv.
set -euo pipefail
cd "$(dirname "$0")"

VENV=".venv"
BUILD_WHEELS="vendor/build-wheels"

# 1. Le venv runtime doit exister.
if [ ! -x "$VENV/bin/python" ]; then
  echo "ERREUR : venv absent. Lancez d'abord ./install_offline.sh" >&2
  exit 1
fi

# 2. Wheels de build requises (aucun téléchargement réseau n'est autorisé).
if [ ! -d "$BUILD_WHEELS" ] || [ -z "$(ls -A "$BUILD_WHEELS" 2>/dev/null)" ]; then
  echo "ERREUR : wheels de build absentes : $BUILD_WHEELS" >&2
  echo "Préparez le kit sur une machine connectée : ./collect_build_wheels.sh" >&2
  exit 1
fi

# 3. Installer PyInstaller hors ligne dans le venv runtime.
"$VENV/bin/python" -m pip install --no-index --no-deps "$BUILD_WHEELS"/*

# 4. Construire l'app (signature ad-hoc par PyInstaller, pas de quarantaine).
"$VENV/bin/pyinstaller" packaging/Jactance.spec

echo
echo "Build terminé : dist/Jactance.app"
echo "Placez le pack à côté de l'app (DEC-0012) : dist/assets/fr-pack/"
echo "Puis lancez dist/Jactance.app (double-clic)."
