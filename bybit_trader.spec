# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_trader_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('.env.example', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'ttkbootstrap', 
        'matplotlib.backends.backend_tkagg',
        'PIL._tkinter_finder',
        'pybit',
        'requests',
        'schedule',
        'colorama',
        'pandas',
        'numpy'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['test', 'tests', 'testing'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BybitCryptoTrader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Окно консоли не показывать
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='trader_icon.ico' if os.path.exists('trader_icon.ico') else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)
