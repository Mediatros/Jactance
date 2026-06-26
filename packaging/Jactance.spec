# -*- mode: python ; coding: utf-8 -*-
# Spec PyInstaller pour Jactance (.app autonome, Apple Silicon, hors ligne).
# Mode onedir + BUNDLE. Le pack de données (modèle) n'est PAS embarqué : il est
# ajouté manuellement dans assets/fr-pack/ à côté du .app (voir src/config.py).
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = [], [], []

# Paquets nécessitant la collecte de leurs binaires/données/sous-modules :
# - mlx        : mlx.metallib (kernels Metal) + libmlx/libjaccl dylib
# - mlx_whisper: assets (mel_filters.npz, *.tiktoken) + timing.py (numba)
# - sounddevice / _sounddevice_data : libportaudio.dylib
# - tiktoken, numba, llvmlite : dépendances transitives compilées
# - rumps : barre de menu
for pkg in (
    "mlx",
    "mlx_whisper",
    "sounddevice",
    "_sounddevice_data",
    "tiktoken",
    "numba",
    "llvmlite",
    "rumps",
):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

hiddenimports += ["_sounddevice", "sounddevice"]

a = Analysis(
    ["../Jactance.py"],
    pathex=[".."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Jactance",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    target_arch="arm64",
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="Jactance",
)

app = BUNDLE(
    coll,
    name="Jactance.app",
    icon=None,
    bundle_identifier="fr.jactance.app",
    info_plist={
        "LSUIElement": True,
        "NSMicrophoneUsageDescription": "Jactance utilise le micro pour la dictee vocale, en local et hors ligne.",
        "CFBundleName": "Jactance",
        "CFBundleDisplayName": "Jactance",
        "NSHighResolutionCapable": True,
        "LSMinimumSystemVersion": "14.0",
    },
)
