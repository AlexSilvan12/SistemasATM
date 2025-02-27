import tkinter as tk
from tkinter import ttk, messagebox
from proveedores import cargar_proveedores, agregar_proveedor

def gestionar_proveedores():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Proveedores")
    ventana.geometry("700x500")
    
    tree = ttk.Treeview(ventana, columns=("ID", "Nombre", "RFC", "Email", "Banco"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Nombre", text="Nombre")
    tree.heading("RFC", text="RFC")
    tree.heading("Email", text="Email")
    tree.heading("Banco", text="Banco")
    tree.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
    
    tk.Button(ventana, text="Agregar Proveedor", command=lambda: agregar_proveedor(tree)).pack()
    cargar_proveedores(tree)
