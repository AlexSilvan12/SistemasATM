import tkinter as tk
from PIL import Image, ImageTk
import os
from proveedores import gestionar_proveedores
from solicitudes import gestionar_solicitudes
from autorizaciones import gestionar_autorizaciones
from usuarios import gestionar_usuarios
import login

LOGO_PATH = os.path.join("plantillas", "LogoATM.png")

# Función para cerrar sesión y volver al login
def cerrar_sesion(ventana):
    ventana.destroy()
    login.ventana_login()

def abrir_menu(rol):
    root = tk.Tk()
    root.geometry("800x600")
    root.configure(bg="white")

    # Cargar logotipo
    try:
        imagen = Image.open(LOGO_PATH)
        imagen = imagen.resize((120, 120), Image.Resampling.LANCZOS)
        logo = ImageTk.PhotoImage(imagen)
        logo_label = tk.Label(root, image=logo, bg="white")
        logo_label.image = logo
        logo_label.pack(pady=10)
    except Exception as e:
        print(f"⚠️ No se pudo cargar el logotipo: {e}")
        
    if rol == "Administrador":
        root.title("Menú Administrador")
        tk.Button(root, text="Gestión de Usuarios", width=30, height=2, command=gestionar_usuarios, font=("Arial", 10, "bold")).pack(pady=10)
        tk.Button(root, text="Gestión de Proveedores", width=30, height=2, command=gestionar_proveedores, font=("Arial", 10, "bold")).pack(pady=10)
        tk.Button(root, text="Gestión de Autorizaciones", width=30, height=2, command=gestionar_autorizaciones, font=("Arial", 10, "bold")).pack(pady=10)
        tk.Button(root, text="Gestión de Solicitudes", width=30, height=2, command=gestionar_solicitudes, font=("Arial", 10, "bold")).pack(pady=10)
    elif rol == "Contador":
        root.title("Menú Contador")
        tk.Button(root, text="Gestión de Solicitudes", width=30, height=2, command=gestionar_solicitudes, font=("Arial", 10, "bold")).pack(pady=10)
        tk.Button(root, text="Gestión de Autorizaciones", width=30, height=2, command=gestionar_autorizaciones, font=("Arial", 10, "bold")).pack(pady=10)
        tk.Button(root, text="Gestión de Proveedores", width=30, height=2, command=gestionar_proveedores, font=("Arial", 10, "bold")).pack(pady=10)
    elif rol == "Comprador":
        root.title("Menú Compras")
        tk.Button(root, text="Gestión de Autorizaciones", width=30, height=2, command=gestionar_autorizaciones, font=("Arial", 10, "bold")).pack(pady=10)
        tk.Button(root, text="Gestión de Solicitudes", width=30, height=2, command=gestionar_solicitudes, font=("Arial", 10, "bold")).pack(pady=10)
        tk.Button(root, text="Gestión de Proveedores", width=30, height=2, command=gestionar_proveedores, font=("Arial", 10, "bold")).pack(pady=10)

    # Botón para cerrar sesión
    tk.Button(root, text="Cerrar sesión", command=lambda: cerrar_sesion(root),
              bg="#cc0000", fg="white", font=("Arial", 10, "bold"), width=15).pack(pady=20)
    
    root.mainloop()