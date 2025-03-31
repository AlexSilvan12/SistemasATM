import tkinter as tk
from PIL import Image, ImageTk
import os
from proveedores import gestionar_proveedores
from solicitudes import gestionar_solicitudes
from autorizaciones import gestionar_autorizaciones
from usuarios import gestionar_usuarios
import login

LOGO_PATH = os.path.join("plantillas", "LogoATM.png")

def cerrar_sesion(ventana):
    """ Cierra la ventana actual y regresa a la pantalla de login """
    ventana.destroy()
    login.ventana_login()

def abrir_menu(rol, ventana_anterior=None):
    """ Abre el menú según el rol del usuario y cierra la ventana anterior si existe """
    if ventana_anterior:
        ventana_anterior.destroy()
    
    root = tk.Tk()
    root.title(f"Menú {rol}")
    root.geometry("800x600")
    root.configure(bg="white")
    root.minsize(800, 600)  # Tamaño mínimo para evitar que se deforme

    # Cargar logotipo
    try:
        imagen = Image.open(LOGO_PATH).resize((120, 120), Image.Resampling.LANCZOS)
        logo = ImageTk.PhotoImage(imagen)
        tk.Label(root, image=logo, bg="white").pack(pady=10)
    except Exception as e:
        print(f"⚠️ No se pudo cargar el logotipo: {e}")

    # Definir botones según el rol
    opciones = {
        "Administrador": [
            ("Gestión de Usuarios", gestionar_usuarios),
            ("Gestión de Proveedores", gestionar_proveedores),
            ("Gestión de Autorizaciones", gestionar_autorizaciones),
            ("Gestión de Solicitudes", gestionar_solicitudes),
        ],
        "Contador": [
            ("Gestión de Solicitudes", gestionar_solicitudes),
            ("Gestión de Autorizaciones", gestionar_autorizaciones),
            ("Gestión de Proveedores", gestionar_proveedores),
        ],
        "Comprador": [
            ("Gestión de Autorizaciones", gestionar_autorizaciones),
            ("Gestión de Solicitudes", gestionar_solicitudes),
            ("Gestión de Proveedores", gestionar_proveedores),
        ]
    }

    for texto, comando in opciones.get(rol, []):
        tk.Button(root, text=texto, width=30, height=2, font=("Arial", 10, "bold"),
                  command=comando).pack(pady=10)

    # Botón para cerrar sesión
    tk.Button(root, text="Cerrar sesión", command=lambda: cerrar_sesion(root),
              bg="#cc0000", fg="white", font=("Arial", 10, "bold"), width=15).pack(pady=10)

    # Botón para salir completamente
    tk.Button(root, text="Salir", command=root.quit, bg="black", fg="white",
              font=("Arial", 10, "bold"), width=15).pack(pady=10)

    root.mainloop()

 
