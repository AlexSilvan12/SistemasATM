
import mysql.connector
from database import conectar_bd

def cargar_proveedores():
    conexion = None
    cursor = None

    try:
        #Conectar a la base de datos
        conexion = conectar_bd()
        if conexion is None:
            print ("❌No se pudo establecer la conexion")
            return
        cursor = conexion.cursor()

        #Se ejecuta la consulta
        query = "SELECT * FROM proveedores"
        cursor.execute(query)
        proveedores = cursor.fetchall()

        #Muestra resultados
        print("✅Lista de Proveedores: ")
        for row in proveedores:
             print (row) 

    except mysql.connector.Error as e:
        print(f"❌Error al cargar proveedores: {e}")

    finally:
        #Cierra el cursos y la conexion si fueron creados correctamente
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()

#Llamar la funcion para probalo
cargar_proveedores()