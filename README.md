# Jactance

Dictée vocale française **100 % hors ligne** pour macOS Apple Silicon (M1 à M5).

Maintien d'une bascule clavier, parole, transcription locale via Whisper MLX,
copie automatique dans le presse-papiers (collage `⌘V` manuel). Conçue pour un
environnement airgap : aucun accès réseau, aucun droit administrateur, tout est
embarqué et exécutable depuis une clé USB.

## Principe

```
Micro -> capture audio (16 kHz mono) -> Whisper MLX (large-v3-turbo)
      -> nettoyage texte -> presse-papiers -> ⌘V manuel
```

Déclencheur : bascule **Ctrl + Command** (démarrer / arrêter), **Échap** pour
annuler. Détection par sondage d'état clavier, sans aucune permission système.

## Installation (hors ligne)

```bash
./install_offline.sh   # crée le venv et installe les dépendances depuis vendor/wheels
./run.sh               # lance l'application
```

Les dépendances s'installent depuis des wheels locales (`vendor/wheels/`), à
préparer au préalable sur une machine connectée :

```bash
./collect_wheels.sh    # télécharge les wheels dans vendor/wheels/
```

## Modèle (ajout manuel)

Le modèle est **dissocié** de l'installation et n'est pas inclus dans ce dépôt
(volumineux, ~1,5 Go). Il s'ajoute manuellement :

1. Récupérer l'archive du modèle `whisper-large-v3-turbo`.
2. Placer le dossier dans `models/` :

   ```
   models/
   └── whisper-large-v3-turbo/
       ├── config.json
       └── weights.safetensors
   ```

Le dossier doit contenir au minimum `config.json` ET `weights.safetensors`.
En cas de modèle absent ou incomplet, l'application affiche un message d'erreur
explicite au démarrage. **Aucun téléchargement n'est jamais effectué.**

## Contraintes

- Aucun appel réseau, aucun téléchargement (y compris au premier lancement).
- Aucun droit administrateur, aucun Homebrew, aucune installation système.
- macOS >= 14.0 requis par MLX.
