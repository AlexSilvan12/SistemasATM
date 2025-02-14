import tkinter as tk
from VProveedores import ventana_gestion_proveedores
from VSolicitudes import ventana_gestion_solicitudes
from VAutorizaciones import ventana_gestion_autorizaciones

def iniciar_interfaz():
    root = tk.Tk()
    root.title("Sistema de Solicitudes de Pago")
    root.geometry("400x300")

    tk.Label(root, text="Menú Principal", font=("Arial", 14)).pack(pady=20)

    btn_proveedores = tk.Button(root, text="Gestión de Proveedores", command=ventana_gestion_proveedores)
    btn_proveedores.pack(pady=5)

    btn_solicitudes = tk.Button(root, text="Gestión de Solicitudes de Pago", command=ventana_gestion_solicitudes)
    btn_solicitudes.pack(pady=5)

    btn_solicitudes = tk.Button(root, text="Gestión de Solicitudes de Pago", command=ventana_gestion_solicitudes)
    btn_solicitudes.pack(pady=5)
    root.mainloop()
