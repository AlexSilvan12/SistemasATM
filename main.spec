# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[
    ('dlls/libmysql.dll', '.')
],
    datas=[
    ('utils.py', '.'),           # Incluye utils.py
    ('database.py', '.'),        # Incluye database
    ('usuarios.py', '.'),        # Incluye usuarios
    ('autorizaciones.py', '.'),  # Incluye autorizaciones
    ('proveedores.py', '.'),     # Incluye proveedores
    ('solicitudes.py', '.'),     # Incluye solicitudes
    ('gerente.py', '.'),         # Incluye gerente
    ('gastos_contrato.py', '.'), # Incluye gastos_contrato
    ('main_menu.py', '.'),       # Incluye main_menu
    ('login.py', '.'),		 #Incluye login
    ('Plantillas/*.png', 'Plantillas'),
    ('Plantillas/*.jpeg', 'Plantillas'),
    ('Plantillas/*.ico', 'Plantillas'),
    ('Plantillas/*.xlsx', 'Plantillas'),
    ('Firmas/*', 'Firmas'),
    ],
    hiddenimports=[
    'mysql.connector.plugins.mysql_native_password',
    'utils',
    'usuarios',
    'autorizaciones',
    'proveedores',
    'solicitudes',
    'gerente',
    'gastos_contrato',
    'main_menu',
    'login',
    'database',
    'mysql',
    'mysql.connector',
    'mysql.connector.locales',
    'mysql.connector.locales.eng',
    ],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon = 'Plantillas/IconoATM.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AppGestor',
)
