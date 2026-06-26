# Guide d'installation (hors ligne)

Installation 100 % hors ligne sur macOS Apple Silicon, sans droit administrateur.
Deux voies, au choix selon la machine :

- **Voie 1 — application pré-buildée** : la plus simple, pour un Mac **non managé**.
- **Voie 2 — build local** : pour un Mac **managé / airgap**, où une app
  téléchargée serait bloquée par la quarantaine Gatekeeper.

## Prérequis

- Mac Apple Silicon, **macOS >= 14.0**.
- Voie 2 uniquement : le `python3` d'Apple (`/usr/bin/python3`, présent par
  défaut). Aucun admin, aucun Homebrew requis.
- Les téléchargements peuvent se faire depuis n'importe quelle machine puis être
  transférés sur la cible (USB ou partage interne).

## Téléchargements

Depuis les **Releases** du dépôt https://github.com/Mediatros/Jactance :

- `fr-pack.zip` (release `fr-pack-v1`, ~1,5 Go) : le pack de données (modèle),
  commun aux deux voies.
- puis, selon la voie :
  - Voie 1 : `Jactance.app.zip` (release `v1.0.0`, ~237 Mo)
  - Voie 2 : `jactance-kit.zip` (release `v1.0.0`, ~112 Mo)

## Voie 1 — Application pré-buildée (Mac non managé)

```bash
unzip Jactance.app.zip                 # -> Jactance.app
unzip fr-pack.zip -d assets/           # -> assets/fr-pack/
```

Disposer l'app et le pack côte à côte (le pack doit être dans le dossier qui
contient l'app) :

```
DictéeLocale/
├── Jactance.app
└── assets/
    └── fr-pack/
```

Lancer par double-clic sur `Jactance.app`. Au premier lancement, macOS peut
afficher « développeur non identifié » : faire **clic droit > Ouvrir**, ou
retirer la quarantaine (sans admin) :

```bash
xattr -dr com.apple.quarantine Jactance.app
```

Si ce retrait est refusé (`Operation not permitted`), la machine est managée :
passer à la **Voie 2**.

## Voie 2 — Build local (Mac managé / airgap)

```bash
unzip jactance-kit.zip                 # -> dossier Jactance/
unzip fr-pack.zip -d Jactance/assets/  # -> Jactance/assets/fr-pack/
cd Jactance
./install_offline.sh   # crée le venv et installe les dépendances (aucun réseau)
./build_app.sh         # construit dist/Jactance.app localement
```

Placer le pack à côté de l'app buildée (`dist/assets/fr-pack/`), puis ouvrir
`dist/Jactance.app`. Le build local évite la quarantaine, donc pas de blocage
ni d'admin.

> Les fichiers issus du téléchargement portent le tag quarantaine, mais cela ne
> gêne ni `pip` ni Python : seules les **apps** lancées par LaunchServices sont
> filtrées. L'app étant **construite sur place**, elle ne porte pas ce tag.

Repli sans construire d'app : exécuter directement depuis les sources avec
`./run.sh`.

## Premier lancement

- macOS demande l'autorisation du **micro** : accepter (sans admin).
- Dicter : **Ctrl + Command** démarre, **Ctrl + Command** arrête,
  **Échap** annule. Le texte est copié dans le presse-papiers, coller avec **⌘V**.

## En cas de problème

- « dossier de wheels absent » (Voie 2) : le `vendor/` du kit n'a pas été
  décompressé au bon endroit (il doit être à côté de `install_offline.sh`).
- « Modèle introuvable / incomplet » : `assets/fr-pack/` manque `config.json`
  ou `weights.safetensors`.
- App qui ne s'ouvre pas (Voie 1) sur Mac managé : utiliser la Voie 2.
- App buildée qui ne s'ouvre pas (Voie 2) : possible politique MDM/EDR au-dessus
  de Gatekeeper ; exécuter depuis les sources (`./run.sh`).

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
