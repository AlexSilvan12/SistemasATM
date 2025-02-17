import tkinter as tk 
from tkinter import ttk, messagebox
#from database import conectar_bd
import usuarios

def ventana_gestion_usuarios():

    ventana = tk.Toplevel()
    ventana.title("Gestión de Usuarios")
    ventana.geometry("400x300")

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

    tk.Button(ventana, text="Agregar Usuario", command=usuarios.agregar_usuario).pack(pady=10)
