# Guide d'installation (hors ligne)

Installation 100 % hors ligne sur macOS Apple Silicon, sans droit administrateur.
Le processus se fait en deux temps : on **prépare le kit** sur une machine
connectée, puis on **installe sur la cible** (hors ligne).

## Prérequis

- Machine de préparation : Mac Apple Silicon **connecté à Internet**.
- Cible : Mac Apple Silicon **macOS >= 14.0**, avec le `python3` d'Apple
  (`/usr/bin/python3`, présent par défaut). Aucun admin, aucun Homebrew requis.

## Étape 1 — Préparer le kit (machine connectée)

```bash
git clone https://github.com/Mediatros/Jactance.git
cd Jactance

# Wheels des dépendances (runtime + build), avec le MÊME Python que la cible
PYTHON_BIN=/usr/bin/python3 ./collect_wheels.sh         # -> vendor/wheels/
PYTHON_BIN=/usr/bin/python3 ./collect_build_wheels.sh   # -> vendor/build-wheels/
```

> Important : forcer `/usr/bin/python3` (3.9). Avec un autre `python3` (ex.
> Homebrew), les wheels seraient incompatibles avec la cible.

Récupérer ensuite le **pack de données** (modèle, ~1,5 Go, hors dépôt) :

1. Télécharger `fr-pack.zip` depuis les **Releases** GitHub du dépôt.
2. Décompresser dans `assets/` : on doit obtenir `assets/fr-pack/config.json`
   et `assets/fr-pack/weights.safetensors`.

Le kit à transférer = le dossier du projet avec `vendor/wheels/`,
`vendor/build-wheels/` et `assets/fr-pack/`.

## Étape 2 — Installer sur la cible (hors ligne)

Transférer le kit sur la cible (USB ou partage interne), puis :

```bash
cd Jactance
./install_offline.sh   # crée le venv et installe les dépendances (aucun réseau)
```

Deux façons de lancer, au choix :

### A. Application autonome (recommandé)

```bash
./build_app.sh         # construit dist/Jactance.app localement
```

Placer le pack à côté de l'app : `dist/assets/fr-pack/`, puis ouvrir
`dist/Jactance.app` (double-clic). Le build local évite la quarantaine
Gatekeeper, donc pas de blocage ni d'admin.

### B. Exécution depuis les sources (repli)

```bash
./run.sh
```

## Premier lancement

- macOS demande l'autorisation du **micro** : accepter (sans admin).
- Dicter : **Ctrl + Command** démarre, **Ctrl + Command** arrête,
  **Échap** annule. Le texte est copié dans le presse-papiers, coller avec **⌘V**.

## En cas de problème

- « dossier de wheels absent » : l'étape 1 n'a pas été faite ou le dossier
  `vendor/` n'a pas été transféré.
- « Modèle introuvable / incomplet » : `assets/fr-pack/` manque `config.json`
  ou `weights.safetensors`.
- App qui ne s'ouvre pas malgré le build local : possible politique MDM/EDR
  au-dessus de Gatekeeper ; utiliser la voie B (`./run.sh`).
