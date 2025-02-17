import mysql.connector

def conectar_bd():
    config = {
        'host':"localhost",
        'user':"root",
        'password':"",
        'database':"sistemasolicitudes",
        'raise_on_warnings': True
    }

    try:
        conexion = mysql.connector.connect(**config)
        return conexion
    except mysql.connector.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

