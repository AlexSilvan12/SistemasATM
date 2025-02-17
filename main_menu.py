import tkinter as tk
from login import ventana_login
from UI.VProveedores import ventana_gestion_proveedores
from UI.VSolicitudes import ventana_gestion_solicitudes
from UI.VAutorizaciones import ventana_gestion_autorizaciones
from UI.VUsuarios import ventana_gestion_usuarios

def abrir_menu(root):
    root.destroy()
    menu = tk.Tk()
    menu.title("Menú Principal")
    menu.geometry("400x300")

    usuario = "admin@example.com"  # Simulación de usuario logueado
    password = "admin123"  # Simulación de contraseña
    rol = ventana_login(usuario, password)

    if rol == "Administrador":
        tk.Button(menu, text="Gestión de Usuarios", command=ventana_gestion_usuarios).pack(pady=5)
        tk.Button(menu, text="Gestión de Proveedores", command=ventana_gestion_proveedores).pack(pady=5)
    elif rol == "Contador":
        tk.Button(menu, text="Gestión de Solicitudes", command=ventana_gestion_solicitudes).pack(pady=5)
        tk.Button(menu, text="Gestión de Proveedores", command=ventana_gestion_proveedores).pack(pady=5)
    elif rol == "Comprador":
        tk.Button(menu, text="Gestión de Autorizaciones", command=ventana_gestion_autorizaciones).pack(pady=5)

    menu.mainloop()

