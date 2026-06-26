# Guide d'installation (hors ligne)

Installation 100 % hors ligne sur macOS Apple Silicon, sans droit administrateur.
Tout le nécessaire est fourni dans les **Releases** GitHub : il suffit de deux
téléchargements, puis l'app se construit **localement sur la cible** (ce qui
évite la quarantaine Gatekeeper).

## Prérequis

- Cible : Mac Apple Silicon **macOS >= 14.0**, avec le `python3` d'Apple
  (`/usr/bin/python3`, présent par défaut). Aucun admin, aucun Homebrew requis.
- Les deux téléchargements peuvent se faire depuis n'importe quelle machine puis
  être transférés sur la cible (USB ou partage interne).

## Étape 1 — Télécharger le kit et le pack

Depuis les **Releases** du dépôt https://github.com/Mediatros/Jactance :

1. `jactance-kit.zip` (release `kit-v2`, ~113 Mo) : code, scripts et toutes les
   dépendances pré-collectées (`vendor/wheels/` et `vendor/build-wheels/`).
2. `fr-pack.zip` (release `fr-pack-v1`, ~1,5 Go) : le pack de données (modèle).

Décompresser le kit, puis y déposer le pack :

```bash
unzip jactance-kit.zip            # -> dossier Jactance/
unzip fr-pack.zip -d Jactance/assets/
```

On doit obtenir `Jactance/assets/fr-pack/config.json` et
`Jactance/assets/fr-pack/weights.safetensors`.

> Les fichiers issus d'un téléchargement portent le tag quarantaine, mais cela
> ne gêne ni `pip` ni Python : seules les **apps** lancées en double-clic sont
> filtrées par Gatekeeper. L'app finale étant **construite sur place**, elle ne
> porte pas ce tag.

## Étape 2 — Installer et construire sur la cible (hors ligne)

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

- « dossier de wheels absent » : le `vendor/` du kit n'a pas été décompressé au
  bon endroit (il doit être à côté de `install_offline.sh`).
- « Modèle introuvable / incomplet » : `assets/fr-pack/` manque `config.json`
  ou `weights.safetensors`.
- App qui ne s'ouvre pas malgré le build local : possible politique MDM/EDR
  au-dessus de Gatekeeper ; utiliser la voie B (`./run.sh`).

## Annexe — Régénérer le kit soi-même (mainteneur)

Pour reconstruire `jactance-kit.zip` à partir des sources, sur un Mac Apple
Silicon **connecté** :

```bash
git clone https://github.com/Mediatros/Jactance.git
cd Jactance
./collect_wheels.sh         # -> vendor/wheels/
./collect_build_wheels.sh   # -> vendor/build-wheels/
```

> Les scripts utilisent par défaut le `python3` d'Apple (3.9) pour produire des
> wheels cp39 compatibles avec la cible. Pour cibler un autre Python, surcharger
> avec `PYTHON_BIN=...`.

Le kit = le dossier du projet avec `vendor/wheels/` et `vendor/build-wheels/`
(le pack de données reste distribué à part).
