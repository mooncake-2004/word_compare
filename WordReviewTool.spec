# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 的 Windows 單文件圖形介面打包設定。"""

from PyInstaller.utils.hooks import collect_all


docx_data, docx_binaries, docx_hidden = collect_all("docx")
lxml_data, lxml_binaries, lxml_hidden = collect_all("lxml")

a = Analysis(
    ["gui.py"],
    pathex=[],
    binaries=docx_binaries + lxml_binaries,
    datas=docx_data + lxml_data,
    hiddenimports=docx_hidden + lxml_hidden,
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
    a.binaries,
    a.datas,
    [],
    name="WordReviewTool",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
