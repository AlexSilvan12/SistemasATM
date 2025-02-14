import tkinter as tk
from tkinter import messagebox
from database import conectar_bd
from UI.main_menu import ventana_menu_principal
import bcrypt

def ventana_login():
    def validar_usuario():
        email = entry_email.get()
        password = entry_password.get()

        if not email or not password:
            messagebox.showwarning("Campos vacíos", "Por favor, ingresa tus credenciales.")
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            query = "SELECT password, rol FROM Usuarios WHERE email = %s"
            cursor.execute(query, (email,))
            resultado = cursor.fetchone()

            if resultado:
                hashed_password, rol = resultado
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                    messagebox.showinfo("Acceso permitido", f"Bienvenido, rol: {rol}")
                    root.destroy()
                    ventana_menu_principal(rol)
                else:
                    messagebox.showerror("Acceso denegado", "Contraseña incorrecta.")
            else:
                messagebox.showerror("Acceso denegado", "Correo no encontrado.")

            cursor.close()
            conexion.close()
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos: {e}")

    root = tk.Tk()
    root.title("Inicio de Sesión")
    root.geometry("700x250")

    tk.Label(root, text="Correo electrónico:").pack(pady=5)
    entry_email = tk.Entry(root, width=30)
    entry_email.pack()

    tk.Label(root, text="Contraseña:").pack(pady=5)
    entry_password = tk.Entry(root, width=30, show="*")
    entry_password.pack()

    tk.Button(root, text="Iniciar Sesión", command=validar_usuario).pack(pady=20)
    root.mainloop()
