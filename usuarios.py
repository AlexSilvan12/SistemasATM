import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar_bd
import mysql.connector
import bcrypt


#funcion para cargar usuarios registrados que no son administradores
def cargar_usuarios():
    conexion = None
    cursor = None

    try:
        # Conectar a la base de datos
        conexion = conectar_bd()
        if conexion is None:
            print("❌No se pudo establecer la conexion")
            return
        cursor = conexion.cursor()

        # Se ejecuta la consulta
        query = "SELECT nombre FROM usuarios WHERE rol <> 'administrador'"
        cursor.execute(query)
        usuarios = [f"{row[0]}" for row in cursor.fetchall()]

        print("✅Usuarios cargados correctamente: ")
        return usuarios
    except mysql.connector.Error as e:
        print(f"❌Error al cargar usuarios: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

#carga informacion de los usuarios en una TreeView
def cargar_usuarios_tree(tree):
    for row in tree.get_children():
        tree.delete(row)  # ✅ Limpia la tabla antes de agregar nuevos datos

    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_usuario, nombre, email, rol, puesto FROM usuarios")
    usuarios = cursor.fetchall()

    for usuario in usuarios:
        tree.insert("", "end", values=usuario)

    cursor.close()
    conexion.close()

#Funcion para modificar los usuarios en la base de datos
def modificar_usuario(id_usuario, nombre, email, rol, puesto, nueva_password, password_actual):
    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        # 🔹 Si el usuario dejó la contraseña en blanco, mantenemos la actual
        password_encrypted = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt()) if nueva_password else password_actual

        query = """
        UPDATE usuarios
        SET nombre = %s, email = %s, password = %s, rol = %s, puesto = %s
        WHERE id_usuario = %s
        """
        valores = (nombre, email, password_encrypted, rol, puesto, id_usuario)
        cursor.execute(query, valores)
        conexion.commit()

        messagebox.showinfo("✅ Éxito", "Usuario modificado correctamente.")
    except mysql.connector.Error as e:
        if conexion:
            conexion.rollback()
        messagebox.showerror("❌ Error", f"Error al modificar usuario: {e}")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


#Funcion para agregar un usuario nuevo
def agregar_usuario(nombre, email, password, rol, puesto, tree):
    if not (nombre and email and password and rol and puesto):
        messagebox.showwarning("Campos vacíos", "Por favor, llena todos los campos.")
        return
    
    password_encrypted = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') if password else None
    
    conexion = None
    cursor = None

    try:
        # Conexión a la base de datos
        conexion = conectar_bd()
        if conexion is None:
            print("❌No se pudo establecer la conexion")
            return
        cursor = conexion.cursor()

        # Ejecuta la consulta
        query = "INSERT INTO Usuarios (nombre, email, password, rol, puesto) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (nombre, email, password_encrypted, rol, puesto))
        conexion.commit()

        messagebox.showinfo("✅Éxito", "Usuario registrado correctamente.")

        cargar_usuarios_tree(tree)
   
    except mysql.connector.Error as e:
        messagebox.showerror("❌Error", "Usuario no agregado: {e}")

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


#Funcion para eliminar usuarios
def eliminar_usuario(tree):
    seleccion = tree.selection()
    if not seleccion:
        messagebox.showwarning("Selecciona un Usuario", "Por favor selecciona un Usuario para eliminar.")
        return

    item = tree.item(seleccion)
    valores = item["values"]
    id_usuario = valores[0]

    confirmacion = messagebox.askyesno("Confirmar eliminación", f"¿Estás seguro de eliminar al usuario con ID {id_usuario}?")
    if not confirmacion:
        return

    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        query = "DELETE FROM usuarios WHERE id_usuario = %s"
        cursor.execute(query, (id_usuario,))
        conexion.commit()

        messagebox.showinfo("✅ Éxito", "Usuario eliminado correctamente.")
        cargar_usuarios_tree(tree)
    except mysql.connector.Error as e:
        if conexion:
            conexion.rollback()
        messagebox.showerror("❌ Error", f"No se pudo eliminar al Usuario: {e}")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

#Ventana para modificar usuarios
def ventana_update(tree):
    seleccion = tree.selection()
    if not seleccion:
        messagebox.showwarning("Selecciona un Usuario", "Por favor selecciona un usuario de la tabla.")
        return

    item = tree.item(seleccion)
    valores = item["values"]
    id_usuario = valores[0]  # El ID está en la primera posición

    # 🔹 Conectar a la BD para obtener la contraseña real
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT password FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    resultado = cursor.fetchone()
    conexion.close()

    password_actual = resultado[0] if resultado else ""  # Si no hay resultado, dejamos vacío

    ventana = tk.Toplevel()
    ventana.title("Modificar Usuario")
    ventana.geometry("400x400")

    # Campos en orden (ahora incluimos la contraseña)
    campos = ["Nombre", "Email", "Rol", "Puesto", "Nueva Contraseña"]
    entradas = []

    for i, campo in enumerate(campos):
        rel_y = 0.05 + i * 0.1
        tk.Label(ventana, text=campo).place(relx=0.05, rely=rel_y)
        entry = tk.Entry(ventana, width=30)
        
        if campo != "Nueva Contraseña":
            entry.insert(0, valores[i + 1])  # Cargamos los datos existentes (excepto password)

        entry.place(relx=0.45, rely=rel_y)
        entradas.append(entry)

    def guardar():
        nuevos_datos = [e.get() for e in entradas]
        nueva_password = nuevos_datos.pop()  # Extraemos la contraseña del final
        modificar_usuario(id_usuario, *nuevos_datos, nueva_password, password_actual)
        ventana.destroy()
        cargar_usuarios_tree(tree)

    tk.Button(ventana, text="Guardar cambios", command=guardar).place(relx=0.35, rely=0.75)


# Ventana para gestionar usuarios
def gestionar_usuarios():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Usuarios")
    ventana.geometry("1100x600")

    # Etiquetas y campos (formulario superior)
    tk.Label(ventana, text="Nombre:").place(relx=0.05, rely=0.05)
    entry_nombre = tk.Entry(ventana)
    entry_nombre.place(relx=0.35, rely=0.05, relwidth=0.6)

    tk.Label(ventana, text="Puesto:").place(relx=0.05, rely=0.15)
    entry_puesto = tk.Entry(ventana)
    entry_puesto.place(relx=0.35, rely=0.15, relwidth=0.6)

    tk.Label(ventana, text="Email:").place(relx=0.05, rely=0.25)
    entry_email = tk.Entry(ventana)
    entry_email.place(relx=0.35, rely=0.25, relwidth=0.6)

    tk.Label(ventana, text="Contraseña:").place(relx=0.05, rely=0.35)
    entry_password = tk.Entry(ventana, show="*")
    entry_password.place(relx=0.35, rely=0.35, relwidth=0.6)

    tk.Label(ventana, text="Rol:").place(relx=0.05, rely=0.45)
    combo_rol = ttk.Combobox(ventana, values=["Administrador", "Contador", "Comprador"])
    combo_rol.place(relx=0.35, rely=0.45, relwidth=0.6)

    # Árbol de usuarios (ajustado para ocupar menos espacio vertical)
    tree = ttk.Treeview(
        ventana,
        columns=("ID", "Nombre", "Email","Rol", "Puesto"),
        show="headings"
    )

    tree.heading("ID", text="ID")
    tree.heading("Nombre", text="Nombre")
    tree.heading("Email", text="Email")
    tree.heading("Rol", text="Rol")
    tree.heading("Puesto", text="Puesto")

    tree.column("ID", width=50)
    tree.column("Nombre", width=250)
    tree.column("Email", width=250)
    tree.column("Rol", width=150)
    tree.column("Puesto", width=120)

    # Ubicar el árbol con menos espacio vertical (ajustando el alto relativo)
    tree.place(relx=0.025, rely=0.55, relwidth=0.95, relheight=0.35)

    # Botones de acción
    tk.Button(ventana, text="Agregar Usuario", command=lambda: agregar_usuario(
        entry_nombre.get(), entry_email.get(), entry_password.get(), combo_rol.get(), entry_puesto.get(),tree)).place(relx=0.2, rely=0.91, relwidth=0.2)
    tk.Button(ventana, text="Modificar Usuario", command=lambda: ventana_update(tree)).place(relx=0.45, rely=0.91, relwidth=0.2)
    tk.Button(ventana, text="Eliminar Usuario", command=lambda: eliminar_usuario(tree)).place(relx=0.7, rely=0.91, relwidth=0.2)

    # Cargar los datos
    cargar_usuarios_tree(tree)
    ventana.mainloop()