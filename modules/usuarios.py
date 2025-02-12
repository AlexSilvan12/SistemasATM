import tkinter as tk
from tkinter import ttk, messagebox
from modules.database import conectar_bd
import bcrypt

def ventana_gestion_usuarios():
    def agregar_usuario():
        nombre = entry_nombre.get()
        email = entry_email.get()
        password = entry_password.get()
        rol = combo_rol.get()

        if not (nombre and email and password and rol):
            messagebox.showwarning("Campos vacíos", "Por favor, llena todos los campos.")
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            query = "INSERT INTO Usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (nombre, email, hashed_password, rol))
            conexion.commit()

            messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
            cursor.close()
            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el usuario: {e}")

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

    tk.Button(ventana, text="Agregar Usuario", command=agregar_usuario).pack(pady=10)
