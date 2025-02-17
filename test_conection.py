
import mysql
from database import conectar_bd

def cargar_proveedores():
    try:
        conexion = conectar_bd()
        query = "SELECT * FROM proveedores"
        cursor = conexion.cursor()
        cursor.execute(query)
        proveedores = cursor.fetchall()

        for row in proveedores:
             print (row) 
    except mysql.connector.Error as e:
        print(f"Error al cargar proveedores: {e}")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

