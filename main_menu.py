import tkinter as tk
from usuarios import ventana_gestion_usuarios
from proveedores import ventana_gestion_proveedores
from autorizaciones import ventana_gestion_autorizaciones
from solicitudes import ventana_gestion_solicitudes_pago

def ventana_menu_principal(rol):
    menu = tk.Tk()
    menu.title("Menú Principal")
    menu.geometry("400x300")

    if rol == "Administrador":
        tk.Label(menu, text="Bienvenido, Administrador").pack(pady=10)
        tk.Button(menu, text="Gestión de Usuarios", command=ventana_gestion_usuarios).pack(pady=5)
        tk.Button(menu, text="Gestión de Proveedores", command=ventana_gestion_proveedores).pack(pady=5)
    elif rol == "Contador":
        tk.Label(menu, text="Bienvenido, Contador").pack(pady=10)
        tk.Button(menu, text="Gestión de Solicitudes de Pago", command=lambda: print("Solicitudes de Pago")).pack(pady=5)
    elif rol == "Comprador":
        tk.Label(menu, text="Bienvenido, Comprador").pack(pady=10)
        tk.Button(menu, text="Gestión de Autorizaciones de Compra", command=ventana_gestion_autorizaciones).pack(pady=5)

    tk.Button(menu, text="Cerrar", command=menu.destroy).pack(pady=20)
    menu.mainloop()
