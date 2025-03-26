import tkinter as tk
from tkinter import messagebox
import mysql.connector
from database import conectar_bd
from PIL import Image, ImageTk
import os


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
    ventana = tk.Tk()
    ventana.title("ATM | Gestor de Pagos y Autorizaciones")
    ventana.geometry("500x400")
    ventana.configure(bg="white")

    # Cargar el logotipo desde la carpeta "plantillas"
    ruta_logo = os.path.join("plantillas", "LogoATM.png")
    if os.path.exists(ruta_logo):
        imagen = Image.open(ruta_logo)
        imagen = imagen.resize((150, 150), Image.Resampling.LANCZOS)
        logo = ImageTk.PhotoImage(imagen)

        label_logo = tk.Label(ventana, image=logo, bg="white")
        label_logo.image = logo  # Referencia para evitar recolección de basura
        label_logo.pack(pady=10)

    # Título grande debajo del logo
    label_titulo = tk.Label(ventana, text="ATM | Gestor de Pagos y Autorizaciones", 
                            font=("Arial", 14, "bold"), bg="white", fg="#1a237e")
    label_titulo.pack(pady=10)

    # Usuario
    tk.Label(ventana, text="Usuario:", bg="white", font=("Arial", 11)).pack(pady=(10, 0))
    entry_usuario = tk.Entry(ventana, width=30)
    entry_usuario.pack()

    # Contraseña
    tk.Label(ventana, text="Contraseña:", bg="white", font=("Arial", 11)).pack(pady=(10, 0))
    entry_contraseña = tk.Entry(ventana, show="*", width=30)
    entry_contraseña.pack()

    tk.Button(ventana, text="Ingresar", command=lambda: validar_usuario(entry_usuario, entry_contraseña, ventana), width=20, bg="#283593", fg="white").pack(pady=20)

    ventana.mainloop()