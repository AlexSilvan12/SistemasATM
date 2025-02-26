from tkinter import ttk
import mysql.connector
from database import conectar_bd
import tkinter as tk


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

        #Muestra resultados (esto es opcional)
        print("✅Lista de Proveedores: ")
        for row in proveedores:
             print (row) 

    except mysql.connector.Error as e:
        print(f"❌Error al cargar proveedores: {e}")

    finally:
        #Cierra el cursor y la conexion si fueron creados correctamente
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()

def agregar_proveedor():
    pass



def gestionar_proveedores():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Proveedores")
    ventana.geometry("700x500")
    tree = ttk.Treeview(ventana, columns=("ID", "Nombre", "RFC", "Email", "Banco"), show="headings")
    tree.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
    tk.Button(ventana, text="Agregar Proveedor", command=agregar_proveedor).pack()
