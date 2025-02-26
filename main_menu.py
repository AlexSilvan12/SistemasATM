import tkinter as tk
from proveedores import gestionar_proveedores
from solicitudes import gestionar_solicitudes
from autorizaciones import gestionar_autorizaciones
from usuarios import gestionar_usuarios


def abrir_menu(rol):
    root = tk.Tk()
    root.title("Menú Principal")
    root.geometry("400x300")
        
    if rol == "Administrador":
        tk.Button(root, text="Gestión de Usuarios", command=gestionar_usuarios).pack()
        tk.Button(root, text="Gestión de Proveedores", command=gestionar_proveedores).pack()
    elif rol == "Contador":
        tk.Button(root, text="Gestión de Solicitudes", command=gestionar_solicitudes).pack()
        tk.Button(root, text="Gestión de Proveedores", command=gestionar_proveedores).pack()
    elif rol == "Comprador":
        tk.Button(root, text="Gestión de Autorizaciones", command=gestionar_autorizaciones).pack()
    
    root.mainloop()
