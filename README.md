# Jactance

Dictée vocale française **100 % hors ligne** pour macOS Apple Silicon (M1 à M5).

Maintien d'une bascule clavier, parole, transcription locale, copie automatique
dans le presse-papiers (collage `⌘V` manuel). Conçue pour un environnement
airgap : aucun accès réseau, aucun droit administrateur, tout est embarqué et
exécutable depuis une clé USB.

## Principe

```
Micro -> capture audio (16 kHz mono) -> moteur de transcription local
      -> nettoyage texte -> presse-papiers -> ⌘V manuel
```

Déclencheur : bascule **Ctrl + Command** (démarrer / arrêter), **Échap** pour
annuler. Détection par sondage d'état clavier, sans aucune permission système.

## Installation (hors ligne)

Guide pas à pas (préparation du kit puis installation sur la cible) : voir
[`INSTALL.md`](INSTALL.md).

```bash
./install_offline.sh   # crée le venv et installe les dépendances depuis vendor/wheels
./run.sh               # lance l'application
```

Les dépendances s'installent depuis des wheels locales (`vendor/wheels/`), à
préparer au préalable sur une machine connectée :

```bash
./collect_wheels.sh    # télécharge les wheels dans vendor/wheels/
```

`collect_wheels.sh` retire du kit `torch` et ses dépendances exclusives
(`sympy`, `networkx`, `mpmath`) : elles sont tirées par le moteur de
transcription mais jamais utilisées à l'exécution (pas d'horodatage mot à mot),
ce qui allège le kit d'environ 340 Mo. L'installation se fait donc en
`--no-deps` (le détail et la justification sont dans `DECISIONS.md`, DEC-0013).

## Application autonome (.app construite localement)

Sur un Mac managé, une `.app` *téléchargée* est bloquée par la quarantaine
Gatekeeper. Une `.app` **construite localement** ne porte pas ce tag et se lance
sans admin ni notarisation. On la fabrique donc sur place, hors ligne :

```bash
./collect_build_wheels.sh   # machine connectée : wheels PyInstaller -> vendor/build-wheels/
./install_offline.sh        # cible : venv runtime
./build_app.sh              # cible : pyinstaller -> dist/Jactance.app
```

Placer ensuite le pack à côté de l'app (`dist/assets/fr-pack/`) puis lancer
`dist/Jactance.app` par double-clic. L'exécution directe depuis les sources
(`./run.sh`) reste disponible en repli. Détail et réserves (politique MDM) dans
`DECISIONS.md`, DEC-0014.

## Pack de données (ajout manuel)

Le pack de transcription est **dissocié** de l'installation et n'est pas inclus
dans ce dépôt (volumineux, ~1,5 Go). Il est fourni en pièce jointe d'une
**Release** GitHub et s'ajoute manuellement :

1. Télécharger l'archive `fr-pack.zip` depuis les Releases du dépôt.
2. Décompresser et placer le dossier dans `assets/` :

   ```
   assets/
   └── fr-pack/
       ├── config.json
       └── weights.safetensors
   ```

Le dossier doit contenir au minimum `config.json` ET `weights.safetensors`.
En cas de pack absent ou incomplet, l'application affiche un message d'erreur
explicite au démarrage. **Aucun téléchargement n'est jamais effectué par l'app.**

## Contraintes

- Aucun appel réseau, aucun téléchargement (y compris au premier lancement).
- Aucun droit administrateur, aucun Homebrew, aucune installation système.
- macOS >= 14.0 requis par le moteur d'inférence.
