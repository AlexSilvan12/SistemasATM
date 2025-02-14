import tkinter as tk
from tkinter import ttk, messagebox
#from database import conectar_bd
import proveedores

def ventana_gestion_proveedores():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Proveedores")
    ventana.geometry("600x400")

    #formulario para agregar proveedor
    tk.Label(ventana, text="Nombre del proveedor:").grid(row=0, column=0, padx=10, pady=5)
    entry_nombre = tk.Entry(ventana)
    entry_nombre.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(ventana, text="RFC:").grid(row=1, column=0, padx=10, pady=5)
    entry_rfc = tk.Entry(ventana)
    entry_rfc.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Email:").grid(row=2, column=0, padx=10, pady=5)
    entry_email = tk.Entry(ventana)
    entry_email.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Clave bancaria:").grid(row=3, column=0, padx=10, pady=5)
    entry_clave_bancaria = tk.Entry(ventana)
    entry_clave_bancaria.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Cuenta bancaria:").grid(row=4, column=0, padx=10, pady=5)
    entry_cuenta_bancaria = tk.Entry(ventana)
    entry_cuenta_bancaria.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Banco:").grid(row=5, column=0, padx=10, pady=5)
    entry_banco = tk.Entry(ventana)
    entry_banco.grid(row=5, column=1, padx=10, pady=5)

    tk.Button(ventana, text="Agregar Proveedor", command=proveedores.agregar_proveedor).grid(row=6, column=0, pady=10)

    tree = ttk.Treeview(ventana, columns=("ID", "Nombre", "RFC", "Email", "Banco"), show="headings")
    tree.grid(row=0, column=0, padx=10, pady=10)

    btn_cargar = tk.Button(ventana, text="Cargar Proveedores", command=lambda: proveedores.cargar_proveedores(tree))
    btn_cargar.grid(row=1, column=0, padx=10, pady=5)

    proveedores.cargar_proveedores(tree)  # Cargar proveedores al abrir la ventana
