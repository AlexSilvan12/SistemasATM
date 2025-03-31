import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar_bd
import mysql.connector
import bcrypt


#funcion para cargar usuarios registrados
def cargar_usuarios():
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
        query = "SELECT nombre FROM usuarios WHERE rol <> 'administrador'"
        cursor.execute(query)
        usuarios = [f"{row[0]}" for row in cursor.fetchall()]
        
        print("✅Usuarios cargados correctamente: ")
        return usuarios
    except mysql.connector.Error as e:
        print(f"❌Error al cargar usuarios: {e}")

    finally:
        #Cierra el cursor y la conexion si fueron creados correctamente
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()


#Funcion para agregar un usuario nuevo
def agregar_usuario(nombre, email, password, rol):

    if not (nombre and email and password and rol):
        messagebox.showwarning("Campos vacíos", "Por favor, llena todos los campos.")
        return
    
    conexion = None
    cursor = None

    try:
        #Conexion a la base de datos
        conexion = conectar_bd()
        if conexion is None:
            print ("❌No se pudo establecer la conexion")
            return
        cursor = conexion.cursor()

        #Ejecuta la consulta
        query = "INSERT INTO Usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (nombre, email, password, rol))
        conexion.commit()

        #Caja con el mensaje de que fue generado correctamente
        messagebox.showinfo("✅Éxito", "Usuario registrado correctamente.")
   
    except mysql.connector.Error as e:
        messagebox.showerror(f"❌Error", "Usuario no agregado", {e})

    finally:
        #Cierra el cursor y la conexion si fueron creados correctamente
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()


#Ventana para agrergar de Usuarios
def gestionar_usuarios():

    ventana = tk.Toplevel()
    ventana.title("Gestión de Usuarios")
    ventana.geometry("800x600")

    tk.Label(ventana, text="Nombre:").pack()
    entry_nombre = tk.Entry(ventana)
    entry_nombre.pack()

    tk.Label(ventana, text="Email:").pack()
    entry_email = tk.Entry(ventana)
    entry_email.pack()

    tk.Label(ventana, text="Contraseña:").pack()
    entry_password = tk.Entry(ventana, show="*")
    entry_password.pack()

    tk.Label(ventana, text="Rol:").pack()
    combo_rol = ttk.Combobox(ventana, values=["Administrador", "Contador", "Comprador"])
    combo_rol.pack()

    tk.Button(ventana, text="Agregar Usuario", command=lambda: agregar_usuario(
        entry_nombre.get(), entry_email.get(), entry_password.get(), combo_rol.get())).pack(pady=10)
    
    
    ventana.mainloop()

 