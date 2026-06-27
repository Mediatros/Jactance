PACK DE DONNÉES JACTANCE (modèle de transcription FR)

Ce dossier contient le pack de données nécessaire à Jactance. Il est volumineux
et distribué séparément de l'application.

INSTALLATION

Le dossier « assets » obtenu après décompression se place à côté de
l'application Jactance.app, dans le même dossier :

    DictéeLocale/
    ├── Jactance.app
    ├── README.txt          (cette notice)
    └── assets/
        └── fr-pack/
            ├── config.json
            └── weights.safetensors

Le dossier « fr-pack » doit contenir au minimum config.json et
weights.safetensors.

FONCTIONNEMENT HORS LIGNE

Jactance n'effectue jamais aucun téléchargement. Si le pack est absent ou
incomplet, l'application affiche un message d'erreur explicite au démarrage.
