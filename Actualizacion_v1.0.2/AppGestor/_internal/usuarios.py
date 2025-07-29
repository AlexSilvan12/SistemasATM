import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar_bd
from utils import ruta_relativa, centrar_ventana, salir
from PIL import Image, ImageTk
import mysql.connector
import os
import bcrypt
from tkinter import filedialog
import shutil

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
        query = "SELECT nombre FROM usuarios"
        cursor.execute(query)
        usuarios = [f"{row[0]}" for row in cursor.fetchall()]

        return usuarios
    except mysql.connector.Error as e:
        print(f"❌Error al cargar usuarios: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

#Obtener el puesto de los usuarios
def puesto_usuario(nombre_usuario):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    query = "SELECT puesto FROM usuarios WHERE nombre = %s"
    cursor.execute(query, (nombre_usuario,))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    return resultado[0] if resultado else ""

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

#Funcion para seleccionar firma desde los archivos
def seleccionar_firma(entry_firma):
    archivo = filedialog.askopenfilename(filetypes=[("Imágenes PNG", "*.png"), ("Todos los archivos", "*.*")])
    if archivo:
        entry_firma.delete(0, tk.END)
        entry_firma.insert(0, archivo)

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
def agregar_usuario(nombre, email, password, rol, puesto, firma_original, tree):
    password_encrypted = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') if password else None

    try:
        # ✅ Crear carpeta de firmas si no existe
        carpeta_firmas = ruta_relativa("Firmas")
        if not os.path.exists(carpeta_firmas):
            os.makedirs(carpeta_firmas)

        # ✅ Generar nombre único para la firma (puede ser con nombre de usuario o email)
        nombre_archivo = f"firma_{nombre.lower().replace(' ', '_')}.png"
        destino = os.path.join(carpeta_firmas, nombre_archivo)

        # ✅ Copiar la firma al destino
        shutil.copy(firma_original, destino)

        # ✅ Guardar solo la ruta relativa
        ruta_firma = os.path.join("Firmas", nombre_archivo)

        # Conexión a la base de datos
        conexion = conectar_bd()
        if conexion is None:
            print("❌No se pudo establecer la conexión")
            return
        cursor = conexion.cursor()

        query = """
            INSERT INTO usuarios (nombre, email, password, rol, puesto, ruta_firma)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nombre, email, password_encrypted, rol, puesto, ruta_firma))
        conexion.commit()

        messagebox.showinfo("✅ Éxito", "Usuario registrado correctamente.")
        cargar_usuarios_tree(tree)

    except Exception as e:
        messagebox.showerror("❌ Error", f"No se pudo registrar el usuario: {e}")
        if conexion:
            conexion.rollback()

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

#Funcion para eliminar usuarios
import os
from tkinter import messagebox
import mysql.connector

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

        # ✅ Obtener ruta de firma
        cursor.execute("SELECT ruta_firma FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        resultado = cursor.fetchone()

        if resultado and resultado[0]:
            ruta_firma_relativa = resultado[0]
            ruta_firma_absoluta = ruta_relativa(ruta_firma_relativa)

            # ✅ Eliminar archivo físico si existe
            if os.path.exists(ruta_firma_absoluta):
                os.remove(ruta_firma_absoluta)

        # ✅ Eliminar usuario de la base de datos
        cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
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

#Interfaz de Usuario
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
    centrar_ventana(ventana, 400, 400)

    # Campos en orden 
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

    tk.Button(ventana, text="Guardar cambios", command=guardar, bg="blue", font=("Arial", 10, "bold")).place(relx=0.4, rely=0.75)
    tk.Button(ventana, text="Cancelar", command= ventana.destroy, font=("Arial", 10,"bold"), bg="red").place(relx=0.2, rely=0.75)

# Ventana para agregar usuarios
def ventana_agregar_usuario(tree):
    ventana = tk.Toplevel()
    ventana.title("Agregar Usuario")
    centrar_ventana(ventana, 600, 300)

    tk.Label(ventana, text="Ingrese los datos del nuevo usuario:", font=("Arial", 12, "bold")).place(relx=0.05, rely=0.05)

    tk.Label(ventana, text="Nombre:", font=("Arial", 10, "bold")).place(relx=0.05, rely=0.15)
    entry_nombre = ttk.Entry(ventana)
    entry_nombre.place(relx=0.15, rely=0.15, relwidth=0.35)

    tk.Label(ventana, text="Puesto:", font=("Arial", 10, "bold")).place(relx=0.05, rely=0.25)
    entry_puesto = ttk.Entry(ventana)
    entry_puesto.place(relx=0.15, rely=0.25, relwidth=0.35)

    tk.Label(ventana, text="Email:", font=("Arial", 10, "bold")).place(relx=0.05, rely=0.35)
    entry_email = ttk.Entry(ventana)
    entry_email.place(relx=0.15, rely=0.335, relwidth=0.35)

    tk.Label(ventana, text="Contraseña:", font=("Arial", 10, "bold")).place(relx=0.05, rely=0.45)
    entry_password = ttk.Entry(ventana)
    entry_password.place(relx=0.20, rely=0.45, relwidth=0.35)

    tk.Label(ventana, text="Rol:", font=("Arial", 10, "bold")).place(relx=0.05, rely=0.55)
    combo_rol = ttk.Combobox(ventana, values=["Administrador", "Contador", "Comprador", "Gerente"])
    combo_rol.place(relx=0.15, rely=0.55, relwidth=0.30)

    tk.Label(ventana, text="Firma (PNG):", font=("Arial", 10, "bold")).place(relx=0.05, rely=0.65)
    entry_firma = ttk.Entry(ventana)
    entry_firma.place(relx=0.20, rely=0.65, relwidth=0.35)
    tk.Button(ventana, text="Seleccionar", command=lambda: seleccionar_firma(entry_firma), font=("Arial", 10,"bold")).place(relx=0.58, rely=0.65, relwidth=0.2)

    def guardar():
        nombre = entry_nombre.get()
        email = entry_email.get()
        password = entry_password.get()
        rol = combo_rol.get()
        puesto = entry_puesto.get()
        firma = entry_firma.get()

        if not all([nombre, email, password, rol, puesto, firma]):
            messagebox.showwarning("Campos incompletos", "Por favor, llena todos los campos antes de guardar.")
            return

        agregar_usuario(nombre, email, password, rol, puesto, firma, tree)
        ventana.destroy()  

    # Botón Guardar
    tk.Button(ventana, text="Guardar", command=guardar, font=("Arial", 10,"bold"), bg="blue").place(relx=0.4, rely=0.85)

    tk.Button(ventana, text="Cancelar", command= ventana.destroy, font=("Arial", 10,"bold"), bg="red").place(relx=0.2, rely=0.85)

def hex_a_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def crear_degradado_vertical(canvas, ancho, alto, color_inicio, color_fin):
    canvas.delete("degradado")  # Limpiar el canvas antes de dibujar un nuevo degradado

    rgb_inicio = hex_a_rgb(color_inicio)
    rgb_fin = hex_a_rgb(color_fin)

    pasos = alto // 2
    for i in range(pasos):
        y = alto - i - 1
        r = int(rgb_inicio[0] + (rgb_fin[0] - rgb_inicio[0]) * i / pasos)
        g = int(rgb_inicio[1] + (rgb_fin[1] - rgb_inicio[1]) * i / pasos)
        b = int(rgb_inicio[2] + (rgb_fin[2] - rgb_inicio[2]) * i / pasos)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, y, ancho, y, fill=color, tags="degradado")

    canvas.create_rectangle(0, 0, ancho, alto // 2, fill=color_fin, outline="", tags="degradado")

def gestionar_usuarios(rol, volver_menu_callback):
    ventana = tk.Tk()
    ventana.title("Gestión de Usuarios")
    centrar_ventana(ventana, 1100, 650)

    # Crear un canvas para el fondo
    canvas = tk.Canvas(ventana)
    canvas.pack(fill="both", expand=True)

    RUTA_LOGO = ruta_relativa("Plantillas/LogoATM.png")
    RUTA_LOGO2 = ruta_relativa("Plantillas/ISO-9001.jpeg")
    RUTA_LOGO3 = ruta_relativa("Plantillas/ISO-14001.jpeg")
    RUTA_LOGO4 = ruta_relativa("Plantillas/ISO-45001.jpeg")
    try:
        # LOGO ATM
        imagen = Image.open(RUTA_LOGO)
        imagen = imagen.resize((120, 160), Image.Resampling.LANCZOS)
        logo_img = ImageTk.PhotoImage(imagen)
        label_logo = tk.Label(canvas, image=logo_img, borderwidth=0)
        label_logo.image = logo_img
        label_logo.place(relx=0.07, rely=0.01)

        # ISO 9001
        iso1 = Image.open(RUTA_LOGO2).resize((70, 70), Image.Resampling.LANCZOS)
        iso1_img = ImageTk.PhotoImage(iso1)
        label_iso1 = tk.Label(canvas, image=iso1_img, borderwidth=0, bg="#ffffff")
        label_iso1.image = iso1_img
        label_iso1.place(relx=0.90, rely=0.01, anchor="ne")  # Esquina inferior derecha

        # ISO 14001
        iso2 = Image.open(RUTA_LOGO3).resize((70, 70), Image.Resampling.LANCZOS)
        iso2_img = ImageTk.PhotoImage(iso2)
        label_iso2 = tk.Label(canvas, image=iso2_img, borderwidth=0, bg="#ffffff")
        label_iso2.image = iso2_img
        label_iso2.place(relx=0.95, rely=0.15, anchor="ne")  # Al lado izquierdo del ISO 9001

        # ISO 45001
        iso3 = Image.open(RUTA_LOGO4).resize((70, 70), Image.Resampling.LANCZOS)
        iso3_img = ImageTk.PhotoImage(iso3)
        label_iso3 = tk.Label(canvas, image=iso3_img, borderwidth=0, bg="#ffffff")
        label_iso3.image = iso3_img
        label_iso3.place(relx=0.85, rely=0.15, anchor="ne")  # Al lado izquierdo del ISO 14001

    except Exception as e:
        print(f"⚠️ No se pudo cargar el logotipo: {e}")
        label_logo = tk.Label(canvas, text="LOGO", font=("Arial", 20, "bold"))
    
    label_titulo = tk.Label(canvas, text="ATM | Gestión de Usuarios",
                            font=("Arial", 20, "bold"), fg="black", bg="white")

    def actualizar_degradado(event):
        # Obtener las dimensiones del canvas (no de la ventana Toplevel)
        ancho = canvas.winfo_width()
        alto = canvas.winfo_height()
        crear_degradado_vertical(canvas, ancho, alto, "#8B0000", "#FFFFFF")

    # Actualizar el fondo degradado al cambiar el tamaño de la ventana
    canvas.bind("<Configure>", actualizar_degradado)

    # Inicializar el degradado en el tamaño actual de la ventana
    ventana.after(100, lambda: actualizar_degradado(None))

    Label_busqueda = tk.Label(ventana, text="Buscar", font=("Arial", 11, "bold"), bg="white")
    entry_busqueda = ttk.Entry(canvas, width=50)

    def buscar_usuarios(*args):  # Acepta *args por el trace
        termino = entry_busqueda.get().lower()
        for item in tree.get_children():
            tree.delete(item)

        conexion = conectar_bd()
        cursor = conexion.cursor()
        consulta = """
            SELECT id_usuario, nombre, email, rol, puesto FROM usuarios
            WHERE LOWER(nombre) LIKE %s
               OR LOWER(email) LIKE %s
               OR LOWER(rol) LIKE %s
               OR LOWER(puesto) LIKE %s
               OR CAST(id_usuario AS CHAR) LIKE %s
        """
        like_termino = f"%{termino}%"
        cursor.execute(consulta, (like_termino, like_termino, like_termino, like_termino, like_termino))
        resultados = cursor.fetchall()
        conexion.close()

        for row in resultados:
            tree.insert("", tk.END, values=row)

    entry_busqueda_var = tk.StringVar()
    entry_busqueda.config(textvariable=entry_busqueda_var)
    entry_busqueda_var.trace("w", buscar_usuarios)  # Búsqueda automática al escribir


    #Aplicacion del estilo a la tabla
    style = ttk.Style()
    style.theme_use("alt")
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"), foreground="white", background="#990000")
    style.map("Treeview.Heading", background=[("!active", "#990000"), ("active", "#990000"), ("pressed", "#990000")],
              foreground=[("!active", "white"), ("active", "white"), ("pressed", "white")])

    # Tabla de usuarios
    tree = ttk.Treeview(
        ventana,
        columns=("ID", "Nombre", "Email", "Rol", "Puesto"),
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
    tree.column("Puesto", width=180)

    # Ubicación de widgets sobre el canvas
    canvas.create_window(550, 380, window=tree, width=1000, height=300)
    tree.place(relx=0.055, rely=0.3, relwidth=0.90, relheight=0.60)
    canvas.create_window(600, 50, window= Label_busqueda)
    Label_busqueda.place(relx=0.28, rely=0.25)
    canvas.create_window(800, 50, window= entry_busqueda)
    entry_busqueda.place(relx=0.35, rely=0.25)
    canvas.create_window(550, 100, window=label_titulo)
    label_titulo.place(relx=0.35, rely=0.10)
    
    # Botones
    tk.Button(ventana, text="Agregar Usuario", command=lambda: ventana_agregar_usuario(tree), font=("Arial", 10,"bold")).place(relx=0.52, rely=0.91, relwidth=0.1, relheight=0.05)
    tk.Button(ventana, text="Modificar Usuario", command=lambda: ventana_update(tree), font=("Arial", 10,"bold")).place(relx=0.65, rely=0.91, relwidth=0.11, relheight=0.05)
    tk.Button(ventana, text="Eliminar Usuario", command=lambda: eliminar_usuario(tree), font=("Arial", 10,"bold")).place(relx=0.78, rely=0.91, relwidth=0.1, relheight=0.05)
    tk.Button(ventana, text="Salir", command= lambda: salir(volver_menu_callback, ventana), bg="red", fg="white", font=("Arial", 10, "bold")).place(relx=0.1, rely=0.92, relwidth=0.08, relheight=0.04)


    # Cargar los datos
    cargar_usuarios_tree(tree)

    ventana.mainloop()