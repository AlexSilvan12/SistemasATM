import mysql.connector

def conectar_bd():
    config = {
        'host':"192.168.1.71",
        'user':"administrador",
        'password':"ATM_4dm1n_25?",
        'database':"sistemasolicitudes",
        'raise_on_warnings': True
    }

    try:
        conexion = mysql.connector.connect(**config)
        return conexion
    except mysql.connector.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

#192.168.1.71
#administrador
#ATM_4dm1n_25?
#localhost
#root