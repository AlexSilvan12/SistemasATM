import mysql.connector

def conectar_bd():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  
            database="sistemasolicitudes"
        )
        return conexion
    except mysql.connector.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        raise
