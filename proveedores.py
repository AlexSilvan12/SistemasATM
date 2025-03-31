from itertools import tee
from tkinter import ttk, messagebox
import mysql.connector
from database import conectar_bd
import tkinter as tk

def cargar_proveedores():
    conexion = None
    cursor = None

    try:
        #Conectar a la base de datos
        conexion = conectar_bd()
        if conexion is None:
            print ("❌No se pudo establecer la conexion")
            return
        cursor = conexion.cursor()

        #Se ejecuta la consulta
        query = "SELECT id_proveedor, nombre FROM proveedores"
        cursor.execute(query)
        proveedores = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]

        #Muestra resultados (esto es opcional)
        print("✅Proveedores cargados correctamente: ")
        
        return proveedores
    except mysql.connector.Error as e:
        print(f"❌Error al cargar proveedores: {e}")

    finally:
        #Cierra el cursor y la conexion si fueron creados correctamente
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()

#Funcion para agregar un nuevo proveedor a la base de datos
def agregar_proveedor(entry_nombre, entry_rfc, entry_email, entry_clave, entry_cuenta, entry_banco, tree, ventana):
    nombre = entry_nombre.get()
    rfc = entry_rfc.get()
    email = entry_email.get()
    clave = entry_clave.get()
    cuenta = entry_cuenta.get()
    banco = entry_banco.get()
    
    if not (nombre and rfc and clave and cuenta and banco):
        messagebox.showwarning("Campos que son obligatorios estan vacíos", "Por favor, llena todos los campos.")
        return
    
    conexion = None
    cursor = None

    try:
        #Conexion con la base de datos
        conexion = conectar_bd()
        if conexion is None:
            print ("❌No se pudo establecer la conexion")
            return
        cursor = conexion.cursor()

        #Ejecuta la consulta
        query = "INSERT INTO Proveedores (nombre, rfc, email, clave_bancaria, cuenta_bancaria, banco) VALUES (%s, %s, %s, %s, %s, %s)"
        valores = (nombre, rfc, email, clave, cuenta, banco)
        cursor.execute(query, valores)
        conexion.commit()

        #Mensaje de exito al agregar y cargar el proveedor nuevo a la tabla
        messagebox.showinfo("✅Éxito", "Proveedor agregado correctamente.")
        gestionar_proveedores.lift()
        gestionar_proveedores.focus_force()
        cargar_proveedores(tree)
        ventana.destroy()

    except mysql.connector.Error as e:
        messagebox.showerror(f"❌Error", "Proveedor no agregado", {e})
    finally:
        #Cierra el cursor y la conexion si fueron creados correctamente
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()

#Carga los proveedores a la tabla
def cargar_proveedores_tree(tree):
    for row in tree.get_children():
        tree.delete(row)  # ✅ Limpia la tabla antes de agregar nuevos datos

    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_proveedor, nombre, rfc, email, clave_bancaria, cuenta_bancaria, banco FROM Proveedores")
    proveedores = cursor.fetchall()

    for proveedor in proveedores:
        tree.insert("", "end", values=proveedor)

    cursor.close()
    conexion.close()

#Funcion para modificar un proveedor
def modificar_proveedor(id_proveedor, nombre, rfc, email, clave_bancaria, cuenta_bancaria, banco):
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        query = """
        UPDATE proveedores
        SET nombre = %s, rfc = %s, email = %s, clave_bancaria = %s, cuenta_bancaria = %s, banco = %s
        WHERE id_proveedor = %s
        """

        valores = (nombre, rfc, email, clave_bancaria, cuenta_bancaria, banco, id_proveedor)
        cursor.execute(query, valores)
        conexion.commit()

        messagebox.showinfo("✅ Éxito", "Proveedor modificado correctamente.")
    except mysql.connector.Error as e:
        if conexion:
            conexion.rollback()
        messagebox.showerror("❌ Error", f"Error al modificar proveedor: {e}")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

#Funcion para eliminar un proveedor de la base de datos
def eliminar_proveedor(tree):
    seleccion = tree.selection()
    if not seleccion:
        messagebox.showwarning("Selecciona un proveedor", "Por favor selecciona un proveedor para eliminar.")
        return

    item = tree.item(seleccion)
    valores = item["values"]
    id_proveedor = valores[0]

    confirmacion = messagebox.askyesno("Confirmar eliminación", f"¿Estás seguro de eliminar al proveedor con ID {id_proveedor}?")
    if not confirmacion:
        return

    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        query = "DELETE FROM proveedores WHERE id_proveedor = %s"
        cursor.execute(query, (id_proveedor,))
        conexion.commit()

        messagebox.showinfo("✅ Éxito", "Proveedor eliminado correctamente.")
        cargar_proveedores_tree(tree)
    except mysql.connector.Error as e:
        if conexion:
            conexion.rollback()
        messagebox.showerror("❌ Error", f"No se pudo eliminar el proveedor: {e}")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def ventana_agregar_proveedor(tree):
    ventana = tk.Toplevel()
    ventana.title("Agregar Proveedor")
    ventana.geometry("800x600")

    # Nombre
    tk.Label(ventana, text="Nombre:").place(relx=0.05, rely=0.05)
    entry_nombre = tk.Entry(ventana, width=30)
    entry_nombre.place(relx=0.45, rely=0.05)

    # RFC
    tk.Label(ventana, text="RFC:").place(relx=0.05, rely=0.15)
    entry_rfc = tk.Entry(ventana, width=30)
    entry_rfc.place(relx=0.45, rely=0.15)

    # Email
    tk.Label(ventana, text="Email:").place(relx=0.05, rely=0.25)
    entry_email = tk.Entry(ventana, width=30)
    entry_email.place(relx=0.45, rely=0.25)

    # Banco
    tk.Label(ventana, text="Banco:").place(relx=0.05, rely=0.35)
    entry_banco = tk.Entry(ventana, width=30)
    entry_banco.place(relx=0.45, rely=0.35)

    # Clave Bancaria
    tk.Label(ventana, text="Clave Bancaria:").place(relx=0.05, rely=0.45)
    entry_clave = tk.Entry(ventana, width=30)
    entry_clave.place(relx=0.45, rely=0.45)

    # Cuenta Bancaria
    tk.Label(ventana, text="Cuenta Bancaria:").place(relx=0.05, rely=0.55)
    entry_cuenta = tk.Entry(ventana, width=30)
    entry_cuenta.place(relx=0.45, rely=0.55)

    # Botón Guardar
    tk.Button(ventana, text="Guardar", command=lambda: agregar_proveedor(
            entry_nombre, entry_rfc, entry_email, entry_banco,
            entry_clave, entry_cuenta, tree, ventana
        )).place(relx=0.4, rely=0.7)

def ventana_update(tree):
    seleccion = tree.selection()
    if not seleccion:
        messagebox.showwarning("Selecciona un proveedor", "Por favor selecciona un proveedor de la tabla.")
        return

    item = tree.item(seleccion)
    valores = item["values"]
    id_proveedor = valores[0]  # Primer campo

    # Crear ventana emergente
    ventana = tk.Toplevel()
    ventana.title("Modificar Proveedor")
    ventana.geometry("400x400")

    # Campos en orden según la tabla
    campos = ["Nombre", "RFC", "Email", "Clave Bancaria", "Cuenta Bancaria", "Banco"]
    entradas = []

    for i, campo in enumerate(campos):
        rel_y = 0.05 + i * 0.1
        tk.Label(ventana, text=campo).place(relx=0.05, rely=rel_y)
        entry = tk.Entry(ventana, width=30)
        entry.insert(0, valores[i + 1])
        entry.place(relx=0.45, rely=rel_y)
        entradas.append(entry)

    def guardar():
        nuevos_datos = [e.get() for e in entradas]
        modificar_proveedor(id_proveedor, *nuevos_datos)
        ventana.destroy()
        cargar_proveedores_tree(tree)

    tk.Button(ventana, text="Guardar cambios", command=guardar).place(relx=0.35, rely=0.75)

#Interfaz de Usuario
def gestionar_proveedores():

    ventana = tk.Toplevel()
    ventana.title("Gestión de Proveedores")
    ventana.geometry("1200x600")

    tk.Label(ventana, text="Buscar:").place(relx=0.02, rely=0.02)
    entry_busqueda = tk.Entry(ventana, width=50)
    entry_busqueda.place(relx=0.1, rely=0.02)

    def buscar_proveedores(*args):  # Acepta *args por el trace
        termino = entry_busqueda.get().lower()
        for item in tree.get_children():
            tree.delete(item)

        conexion = conectar_bd()
        cursor = conexion.cursor()
        consulta = """
            SELECT * FROM proveedores
            WHERE LOWER(nombre) LIKE %s
               OR LOWER(rfc) LIKE %s
               OR LOWER(email) LIKE %s
               OR LOWER(banco) LIKE %s
        """
        like_termino = f"%{termino}%"
        cursor.execute(consulta, (like_termino, like_termino, like_termino, like_termino))
        resultados = cursor.fetchall()
        conexion.close()

        for row in resultados:
            tree.insert("", tk.END, values=row)

    entry_busqueda_var = tk.StringVar()
    entry_busqueda.config(textvariable=entry_busqueda_var)
    entry_busqueda_var.trace("w", buscar_proveedores)  # Búsqueda automática al escribir

    tree = ttk.Treeview(
        ventana,
        columns=("ID", "Nombre", "RFC", "Email", "Clave", "Cuenta", "Banco"),
        show="headings"
    )

    tree.heading("ID", text="ID")
    tree.heading("Nombre", text="Nombre")
    tree.heading("RFC", text="RFC")
    tree.heading("Email", text="Email")
    tree.heading("Clave", text="Clave Bancaria")
    tree.heading("Cuenta", text="Cuenta Bancaria")
    tree.heading("Banco", text="Banco")

    tree.column("ID", width=50)
    tree.column("Nombre", width=250)
    tree.column("RFC", width=100)
    tree.column("Email", width=250)
    tree.column("Clave", width=150)
    tree.column("Cuenta", width=120)
    tree.column("Banco", width=100)

    tree.place(relx=0.025, rely=0.1, relwidth=0.95, relheight=0.75)

    tk.Button(ventana, text="Agregar Proveedor", command=lambda: ventana_agregar_proveedor(tree)).place(relx=0.1, rely=0.85)
    tk.Button(ventana, text="Modificar proveedor", command=lambda: ventana_update(tree)).place(relx=0.4, rely=0.85)
    tk.Button(ventana, text="Eliminar proveedor", command=lambda: eliminar_proveedor(tree)).place(relx=0.7, rely=0.85)
  
    cargar_proveedores_tree(tree)
    ventana.mainloop()
 