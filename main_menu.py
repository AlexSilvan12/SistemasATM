import tkinter as tk
from proveedores import gestionar_proveedores
from solicitudes import gestionar_solicitudes
from autorizaciones import gestionar_autorizaciones
from usuarios import gestionar_usuarios


def abrir_menu(rol):
    root = tk.Tk()
    root.geometry("400x300")
        
    if rol == "Administrador":
        root.title("Menú Administrador")
        tk.Button(root, text="Gestión de Usuarios", command=gestionar_usuarios).pack(pady=10)
        tk.Button(root, text="Gestión de Proveedores", command=gestionar_proveedores).pack(pady=10)
    elif rol == "Contador":
        root.title("Menú Contador")
        tk.Button(root, text="Gestión de Solicitudes", command=gestionar_solicitudes).pack(pady=10)
        tk.Button(root, text="Gestión de Proveedores", command=gestionar_proveedores).pack(pady=10)
    elif rol == "Comprador":
        root.title("Menú Compras")
        tk.Button(root, text="Gestión de Autorizaciones", command=gestionar_autorizaciones).pack(pady=10)
        tk.Button(root, text="Gestión de Proveedores", command=gestionar_proveedores).pack(pady=10)
    
    root.mainloop()
