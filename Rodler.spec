# Rodler.spec
# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# Carpeta base del proyecto: donde ejecutás "pyinstaller Rodler.spec"
BASE_DIR = os.getcwd()
CONFIG_PATH = os.path.join(BASE_DIR, "config.ini")

a = Analysis(
    ['main\\login_ui.py'],
    pathex=[BASE_DIR],
    binaries=[],
    datas=[
        ('rodlerIcons', 'rodlerIcons'),
        ('ui', 'ui'),
        ('db/Scripts', 'db/Scripts'),
        ('graficos', 'graficos'),
        (CONFIG_PATH, '.'),
    ],
    hiddenimports=[
        'db.conexion',
        'db.clientes_queries',
        'db.compras_queries',
        'db.empleados_queries',
        'db.prov_queries',
        'db.ventas_queries',
        'main.MenuPrincipal',
        'Rodler_auth',
        'themes',
        'graficos.graficos_dashboard',
        'graficos.graficos_dashboard2',
        'graficos.graficos_style',
        'graficos.plotly_themes',
        'services.weather',
    ],
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
    name='Rodler',
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
    icon=[os.path.join(BASE_DIR, 'rodlerIcons', 'app_logo.ico')],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Rodler',
)
