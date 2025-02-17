import tkinter as tk
from tkinter import ttk, messagebox
from proveedores import cargar_proveedores, agregar_proveedor

def ventana_gestion_proveedores():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Proveedores")
    ventana.geometry("700x500")

    tree = ttk.Treeview(ventana, columns=("ID", "Nombre", "RFC", "Email", "Banco"), show="headings")
    tree.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
    
    def actualizar_tabla():
        for row in tree.get_children():
            tree.delete(row)
        for proveedor in cargar_proveedores():
            tree.insert("", "end", values=proveedor)
    
    actualizar_tabla()

    tk.Label(ventana, text="Nombre: ").grid(row=1, column=0)
    entry_nombre = tk.Entry(ventana)
    entry_nombre.grid(row=1, column=1)
    
    def guardar():
        if agregar_proveedor(entry_nombre.get(), "RFC", "email", "banco"):
            actualizar_tabla()
            messagebox.showinfo("Éxito", "Proveedor agregado")
    
    tk.Button(ventana, text="Agregar", command=guardar).grid(row=2, column=0, columnspan=2)
