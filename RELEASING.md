# Versionnage et publication

> Règle figée : chaque évolution de l'appli donne lieu à une release `vX.Y.Z`
> publiant **les deux approches** (application pré-buildée `Jactance.app.zip` ET
> kit sources `jactance-kit.zip`). Voir aussi `CLAUDE.md`.

## Schéma de version (SemVer)

Tags au format `vMAJEUR.MINEUR.CORRECTIF` :

- **CORRECTIF** (`v1.0.0` → `v1.0.1`) : correction de bug, sans nouvelle
  fonctionnalité ni rupture.
- **MINEUR** (`v1.0.0` → `v1.1.0`) : ajout de fonctionnalité rétrocompatible.
- **MAJEUR** (`v1.x` → `v2.0.0`) : changement majeur ou rupture de compatibilité.

## Releases

### Release applicative `vX.Y.Z`

Une release par version, contenant **deux moyens de récupération** :

- `Jactance.app.zip` : l'application pré-buildée (Voie 1, Mac non managé).
- `jactance-kit.zip` : sources + dépendances pré-collectées, pour le build local
  (Voie 2, Mac managé / airgap).

### Release du pack de données

Le modèle suit sa **propre version** (`fr-pack-v1`, `fr-pack-v2`…), indépendante
du code : il est volumineux (~1,5 Go) et change rarement. La compatibilité
pack ↔ application est indiquée dans les notes de release.

Le zip est structuré pour se décompresser directement en `assets/fr-pack/`
(aucune création manuelle du dossier `assets/`) et embarque la notice
`packaging/fr-pack-README.txt`, renommée `README.txt`, à côté du dossier
`assets/`. Arborescence du zip :

```
assets/
└── fr-pack/
    ├── config.json
    └── weights.safetensors
README.txt
```

Fabrication (le pack n'est pas dans le dépôt) :

```bash
STAGE=$(mktemp -d)
mkdir -p "$STAGE/assets"
cp -R /chemin/vers/fr-pack "$STAGE/assets/fr-pack"
cp packaging/fr-pack-README.txt "$STAGE/README.txt"
( cd "$STAGE" && zip -r -q -X fr-pack.zip assets README.txt )
```

## Fabriquer une release applicative

Sur un Mac Apple Silicon connecté, depuis un dépôt à jour :

```bash
# 1. Dépendances pré-collectées (python3 d'Apple par défaut -> wheels cp39)
./collect_wheels.sh
./collect_build_wheels.sh

# 2. Kit = contenu suivi (git archive) + wheels
STAGE=$(mktemp -d)/Jactance
git archive --format=tar HEAD | (mkdir -p "$STAGE" && tar -x -C "$STAGE")
cp -R vendor/wheels vendor/build-wheels "$STAGE/vendor/"
( cd "$(dirname "$STAGE")" && zip -r -q -X jactance-kit.zip Jactance )

# 3. App pré-buildée
./install_offline.sh && ./build_app.sh
( cd dist && zip -r -q -X Jactance.app.zip Jactance.app )

# 4. Publier (remplacer X.Y.Z)
gh release create vX.Y.Z \
  "$(dirname "$STAGE")/jactance-kit.zip" \
  dist/Jactance.app.zip \
  --title "Jactance vX.Y.Z" --notes "..."
```

Le kit est construit via `git archive` : il ne contient donc que le code suivi
(ni modèle, ni fichiers de pilotage, ni `.git`/`.venv`).
