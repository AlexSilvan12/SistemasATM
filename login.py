import tkinter as tk
from tkinter import messagebox
import mysql.connector
from database import conectar_bd


def verificar_credenciales(email, password):

    if not email or not password:
         messagebox.showwarning("Campos vacíos", "Por favor, ingresa tus credenciales.")
         return
        
    conexion = None
    cursor = None

    try:
        #conectar a la base de datos
        conexion = conectar_bd()
        if conexion is None:
            print ("❌No se pudo establecer la conexion")
            return
        cursor = conexion.cursor()

        #Ejecutar consulta
        query = "SELECT rol FROM Usuarios WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        resultado = cursor.fetchone()

        #Compara los datos ingresados con la base de datos
        return resultado[0] if resultado else None
    
    except mysql.connector.Error as e:
             messagebox.showerror("❌Error de conexión", f"No se pudo conectar a la base de datos: {e}")

    finally:
    #Cierra el cursor y la conexion si fueron creados correctamente
     if cursor is not None:
        cursor.close()
     if conexion is not None:
        conexion.close()  

#Funcion para manejar la logica de la GUI
def validar_usuario(entry_email, entry_password, root):

    from main_menu import abrir_menu

    #Recibe los datos desde la intefaz
    email = entry_email.get()
    password = entry_password.get()
    rol = verificar_credenciales(email, password)

    #Condicion para abrir el menú especifico segun el rol
    if rol:
        root.destroy()
        abrir_menu(rol)
    else:
        messagebox.showerror("❌Error", "Credenciales incorrectas")


#GUI
def ventana_login():

    root = tk.Tk()
    root.title("Inicio de Sesión")
    
    tk.Label(root, text="Usuario:").pack()
    entry_usuario = tk.Entry(root)
    entry_usuario.pack()

    tk.Label(root, text="Contraseña:").pack()
    entry_password = tk.Entry(root, show="*")
    entry_password.pack()

    tk.Button(root, text="Ingresar", command=lambda: validar_usuario(entry_usuario, entry_password, root)).pack()
    
    root.mainloop()

