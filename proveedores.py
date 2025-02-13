import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar_bd

# Ventana para la gestión de proveedores
def ventana_gestion_proveedores():
    def agregar_proveedor():
        nombre = entry_nombre.get()
        rfc = entry_rfc.get()
        email = entry_email.get()
        clave_bancaria = entry_clave_bancaria.get()
        cuenta_bancaria = entry_cuenta_bancaria.get()
        banco = entry_banco.get()

        if not (nombre and rfc and clave_bancaria and cuenta_bancaria and banco):
            messagebox.showwarning("Campos vacíos", "Por favor, llena todos los campos obligatorios.")
            return

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            query = """
            INSERT INTO Proveedores (nombre, rfc, email, clave_bancaria, cuenta_bancaria, banco)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            valores = (nombre, rfc, email, clave_bancaria, cuenta_bancaria, banco)
            cursor.execute(query, valores)
            conexion.commit()

            messagebox.showinfo("Éxito", "Proveedor registrado correctamente.")
            limpiar_formulario()
            cargar_proveedores()

            cursor.close()
            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el proveedor: {e}")

    def cargar_proveedores():
        for row in tree.get_children():
            tree.delete(row)

        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_proveedor, nombre, rfc, email, banco FROM Proveedores")
            for proveedor in cursor.fetchall():
                tree.insert("", "end", values=proveedor)

            cursor.close()
            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los proveedores: {e}")

    def limpiar_formulario():
        entry_nombre.delete(0, tk.END)
        entry_rfc.delete(0, tk.END)
        entry_email.delete(0, tk.END)
        entry_clave_bancaria.delete(0, tk.END)
        entry_cuenta_bancaria.delete(0, tk.END)
        entry_banco.delete(0, tk.END)

    ventana = tk.Toplevel()
    ventana.title("Gestión de Proveedores")
    ventana.geometry("800x600")

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

    tk.Button(ventana, text="Agregar Proveedor", command=agregar_proveedor).grid(row=6, column=0, pady=10)

    columnas = ("ID", "Nombre", "RFC", "Email", "Banco")
    tree = ttk.Treeview(ventana, columns=columnas, show="headings")
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor="center")

    tree.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

