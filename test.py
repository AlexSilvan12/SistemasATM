from database import conectar_bd

conexion = conectar_bd()
if conexion:
    conexion.close()
    print("✅ La conexión se cerró correctamente.")
else:
    print("❌ Falló la conexión a la base de datos.")