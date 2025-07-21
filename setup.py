from setuptools import setup
import glob

APP = ['main.py']
DATA_FILES = [
    ('Firmas', ['Firmas/firma_alejandro_silvan.png',
                'Firmas/firma_comprador1.png',
                'Firmas/firma_contador_1.png',
                'Firmas/firma_dalia_guzman_palomino.png']),
    ('Plantillas', []),  # Se completará abajo con glob
]

# Agrega archivos de la carpeta Plantillas
plantillas_archivos = glob.glob('Plantillas/*.png') + \
                      glob.glob('Plantillas/*.jpeg') + \
                      glob.glob('Plantillas/*.ico') + \
                      glob.glob('Plantillas/*.xlsx')
DATA_FILES.append(('Plantillas', plantillas_archivos))

OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'Plantillas/IconoATM.icns',
    'packages': [
        'tkcalendar',
        'openpyxl',
        'Pillow',
        'bcrypt',
        'mysql',
        'mysql.connector'
    ],
    'includes': [
        'tkinter',
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
        'mysql.connector.locales.eng'
    ],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
