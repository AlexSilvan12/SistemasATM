from itertools import tee
from tkinter import ttk, messagebox
import mysql.connector
from database import conectar_bd
import tkinter as tk


def gestionar_proveedores():

    ventana = tk.Toplevel()
    ventana.title("Gestión de Proveedores")
    ventana.geometry("700x500")
    
    tree = ttk.Treeview(ventana, columns=("ID", "Nombre", "RFC", "Email", "Banco"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Nombre", text="Nombre")
    tree.heading("RFC", text="RFC")
    tree.heading("Email", text="Email")
    tree.heading("Banco", text="Banco")
    tree.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
    
    tk.Button(ventana, text="Agregar Proveedor", command=lambda: ventana_agregar_proveedor(tree)).pack()
    cargar_proveedores(tree)

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
        query = "SELECT id_proveedor, nombre, rfc, email, banco FROM proveedores"
        cursor.execute(query)
        proveedores = cursor.fetchall()

        #Muestra resultados (esto es opcional)
        print("✅Proveedores cargados correctamente: ")
         
    except mysql.connector.Error as e:
        print(f"❌Error al cargar proveedores: {e}")

    finally:
        #Cierra el cursor y la conexion si fueron creados correctamente
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()

def ventana_agregar_proveedor(tree):

    ventana = tk.Toplevel()
    ventana.title("Agregar Proveedor")
    
    tk.Label(ventana, text="Nombre:").grid(row=0, column=0)
    entry_nombre = tk.Entry(ventana)
    entry_nombre.grid(row=0, column=1)
    
    tk.Label(ventana, text="RFC:").grid(row=1, column=0)
    entry_rfc = tk.Entry(ventana)
    entry_rfc.grid(row=1, column=1)
    
    tk.Label(ventana, text="Email:").grid(row=2, column=0)
    entry_email = tk.Entry(ventana)
    entry_email.grid(row=2, column=1)
    
    tk.Label(ventana, text="Banco:").grid(row=3, column=0)
    entry_banco = tk.Entry(ventana)
    entry_banco.grid(row=3, column=1)

    tk.Label(ventana, text="Clave Bancara:").grid(row=4, column=0)
    entry_clave = tk.Entry(ventana)
    entry_clave.grid(row=4, column=1)
    
    tk.Label(ventana, text="Cuenta Bancara:").grid(row=5, column=0)
    entry_cuenta = tk.Entry(ventana)
    entry_cuenta.grid(row=5, column=1)

    tk.Button(ventana, text="Guardar", command=lambda: agregar_proveedor(entry_nombre, entry_rfc, entry_email, entry_banco, tree, ventana)).grid(row=5, column=0, columnspan=2)

#Funcion para agregar un nuevo proveedor a la base de datos 
def agregar_proveedor(entry_nombre, entry_rfc, entry_email, entry_clave, entry_cuenta, entry_banco, tree, ventana):
    nombre = entry_nombre.get()
    rfc = entry_rfc.get()
    email = entry_email.get()
    clave = entry_clave.get()
    cuenta = entry_cuenta.get()
    banco = entry_banco.get()
    
    if not (nombre and rfc and clave and cuenta and banco):
        messagebox.showwarning("Campos que son obligatorios estan vacíos", "Por favor, llena todos los campos.")
        return
    
    conexion = None
    cursor = None

    try:
        #Conexion con la base de datos
        conexion = conectar_bd()
        if conexion is None:
            print ("❌No se pudo establecer la conexion")
            return
        cursor = conexion.cursor()

        #Ejecuta la consulta
        query = "INSERT INTO Proveedores (nombre, rfc, email, clave_bancaria, cuenta_bancaria, banco) VALUES (%s, %s, %s, %s, %s, %s)"
        valores = (nombre, rfc, email, banco)
        cursor.execute(query, valores)
        conexion.commit()

        #Mensaje de exito al agregar y cargar el proveedor nuevo a la tabla
        messagebox.showinfo("✅Éxito", "Proveedor agregado correctamente.")
        cargar_proveedores(tree)
        ventana.destroy()

    except mysql.connector.Error as e:
        messagebox.showinfo(f"❌Error", "Proveedor no agregado", {e})
    finally:
        #Cierra el cursor y la conexion si fueron creados correctamente
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()