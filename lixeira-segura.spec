# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files


datas = []

datas += collect_data_files("customtkinter")

datas += [
    ("icon/icone.png", "icon")
]


hiddenimports = [
    "customtkinter",
    "PIL",
    "PIL.Image",
    "darkdetect",
    "packaging"
]


a = Analysis(
    ["lixeira_segura.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name="lixeira-segura",
    debug=False,
    strip=False,
    upx=True,
    console=False
)


coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="lixeira-segura"
)

