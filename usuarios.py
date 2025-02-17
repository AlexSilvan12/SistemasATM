import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar_bd
import bcrypt


def agregar_usuario(nombre, email, password, rol):

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