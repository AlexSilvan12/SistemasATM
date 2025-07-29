import mysql.connector
from mysql.connector import Error

# Cambia estos valores si es necesario
HOST = "alejandrosram.ddns-ip.net"  # ← tu subdominio DDNS
PUERTO = 3306                       # o el puerto externo que abriste
USUARIO = "administrador"
CONTRASENA = "ATM_4dm1n_25?"
BASEDATOS = "sistemasolicitudes"

try:
    conexion = mysql.connector.connect(
        host=HOST,
        port=PUERTO,
        user=USUARIO,
        password=CONTRASENA,
        database=BASEDATOS,
        auth_plugin='mysql_native_password',
        connect_timeout=5
    )

    if conexion.is_connected():
        print("✅ Conexión exitosa a la base de datos usando el subdominio DDNS.")
        cursor = conexion.cursor()
        cursor.execute("SHOW TABLES;")
        tablas = cursor.fetchall()
        print("📋 Tablas encontradas:", [t[0] for t in tablas])
        cursor.close()
        conexion.close()
    else:
        print("❌ No se pudo conectar a la base de datos.")

except Error as e:
    print(f"❌ Error al conectar a MySQL: {e}")

