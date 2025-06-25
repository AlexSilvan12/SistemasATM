from PyInstaller.utils.hooks import collect_data_files

#Incluye posibles dependencias y locales
data = collect_data_files('mysql.connector', include_py_files= True)
hiddenimports = [
    'mysql.connector.locales',
    'mysql.connector.locales.eng',
    '_cffi_backend'
]

