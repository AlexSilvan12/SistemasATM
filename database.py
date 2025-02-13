import _mysql_connector

def conectar_bd():
    try:
        conexion = _mysql_connector(
            host="localhost",
            user="root",
            password="",  
            database="sistemasolicitudes"
        )
        return conexion
    except _mysql_connector.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        raise
