import mysql.connector
from mysql.connector import Error

# CONFIGURA ESTOS DATOS
IP_PUBLICA = "189.230.154.61"                                  
PUERTO = 3306                      # O el puerto externo que abriste (ej. 5306)
USUARIO = "administrador"          # Usuario MySQL con permisos remotos
CONTRASENA = "ATM_4dm1n_25?"
BASE_DATOS = "sistemasolicitudes"

try:
    conexion = mysql.connector.connect(
        host=IP_PUBLICA,
        port=PUERTO,
        user=USUARIO,
        password=CONTRASENA,
        database=BASE_DATOS,
        auth_plugin='mysql_native_password'
    )

    if conexion.is_connected():
        print("✅ Conexión exitosa a la base de datos.")
        cursor = conexion.cursor()
        cursor.execute("SHOW TABLES;")
        tablas = cursor.fetchall()
        print("📋 Tablas encontradas:", tablas)
        cursor.close()
        conexion.close()
    else:
        print("❌ No se pudo conectar a la base de datos.")

except Error as e:
    print(f"❌ Error de conexión: {e}")

