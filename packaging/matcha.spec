# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for the single-file `matcha` CLI binary.

Build from the repo root:
    pyinstaller packaging/matcha.spec --clean --noconfirm

Entry point is matcha/cli.py (its `__main__` shim calls the typer `app`);
absolute imports inside the package resolve via `pathex` pointing at the
repo root.
"""
import os

ROOT = os.path.abspath(os.path.join(SPECPATH, os.pardir))

a = Analysis(
    [os.path.join(ROOT, "matcha", "cli.py")],
    pathex=[ROOT],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="matcha",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
