import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar_bd

# Ventana para la gestión de proveedores
def agregar_proveedor(nombre, rfc, email, banco, clave_bancaria, cuenta_bancaria):
      
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
          
            cargar_proveedores()

            cursor.close()
            conexion.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el proveedor: {e}")

def cargar_proveedores():
    try:
        conexion = conectar_bd()
        query = "SELECT * FROM proveedores"
        cursor = conexion.cursor()
        cursor.execute(query)
        proveedores = cursor.fetchall()

        for row in proveedores:
             print (row)
             
        cursor.close()
        conexion.close()
        return proveedores
    except Exception as e:
        print(f"Error al cargar proveedores: {e}")
        return []

