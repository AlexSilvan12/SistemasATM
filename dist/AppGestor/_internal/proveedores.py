from tkinter import ttk, messagebox
from PIL import Image, ImageTk 
import mysql.connector
from database import conectar_bd
from utils import ruta_relativa, centrar_ventana, salir
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
    centrar_ventana(ventana, 400, 400)

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

    tk.Button(ventana, text="Guardar cambios", command=guardar, font=("Arial", 10,"bold"), bg="blue").place(relx=0.4, rely=0.75)
    tk.Button(ventana, text="Cancelar", command= ventana.destroy, font=("Arial", 10,"bold"), bg="red").place(relx=0.2, rely=0.75)


#Interfaz de Usuario
def ventana_agregar_proveedor(tree):
    ventana = tk.Toplevel()
    ventana.title("Agregar Proveedor")
    centrar_ventana(ventana, 600, 300)

    tk.Label(ventana, text="Ingrese los datos del nuevo Proveedor:", font=("Arial", 12, "bold")).place(relx=0.05, rely=0.05)

    # Nombre
    tk.Label(ventana, text="Nombre:", font=("Arial", 10, "bold")).place(relx=0.05, rely=0.15)
    entry_nombre = tk.Entry(ventana, width=30)
    entry_nombre.place(relx=0.15, rely=0.15)

    # RFC
    tk.Label(ventana, text="RFC:", font=("Arial", 10, "bold")).place(relx=0.05, rely=0.25)
    entry_rfc = tk.Entry(ventana, width=30)
    entry_rfc.place(relx=0.15, rely=0.25)

    # Email
    tk.Label(ventana, text="Email:", font=("Arial", 10, "bold")).place(relx=0.05, rely=0.35)
    entry_email = tk.Entry(ventana, width=30)
    entry_email.place(relx=0.15, rely=0.35)

    # Banco
    tk.Label(ventana, text="Banco:", font=("Arial", 10, "bold")).place(relx=0.05, rely=0.45)
    entry_banco = tk.Entry(ventana, width=30)
    entry_banco.place(relx=0.15, rely=0.45)

    # Clave Bancaria
    tk.Label(ventana, text="Clave Bancaria:", font=("Arial", 10, "bold")).place(relx=0.05, rely=0.55)
    entry_clave = tk.Entry(ventana, width=30)
    entry_clave.place(relx=0.25, rely=0.55)

    # Cuenta Bancaria
    tk.Label(ventana, text="Cuenta Bancaria:", font=("Arial", 10, "bold")).place(relx=0.05, rely=0.65)
    entry_cuenta = tk.Entry(ventana, width=30)
    entry_cuenta.place(relx=0.25, rely=0.65)

    # Botón Guardar
    tk.Button(ventana, text="Guardar", command=lambda: agregar_proveedor(
            entry_nombre, entry_rfc, entry_email, entry_banco,
            entry_clave, entry_cuenta, tree, ventana
        ), font=("Arial", 10,"bold"), bg="blue").place(relx=0.4, rely=0.85 )
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

def gestionar_proveedores(rol, volver_menu_callback):

    ventana = tk.Tk()
    ventana.title("Gestión de Proveedores")
    centrar_ventana(ventana, 1200, 600)

    tk.Label(ventana, text="Buscar:").place(relx=0.02, rely=0.02)
    entry_busqueda = tk.Entry(ventana, width=50)
    entry_busqueda.place(relx=0.1, rely=0.02)

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
        imagen = imagen.resize((150, 160), Image.Resampling.LANCZOS)
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
    
    label_titulo = tk.Label(canvas, text="ATM | Gestión de Proveedores",
                            font=("Arial", 20, "bold"), fg="black", bg="white")
    
    def actualizar_degradado(event):
        # Obtener las dimensiones del canvas
        ancho = canvas.winfo_width()
        alto = canvas.winfo_height()
        crear_degradado_vertical(canvas, ancho, alto, "#8B0000", "#FFFFFF")

    # Actualizar el fondo degradado al cambiar el tamaño de la ventana
    canvas.bind("<Configure>", actualizar_degradado)

    # Inicializar el degradado en el tamaño actual de la ventana
    ventana.after(100, lambda: actualizar_degradado(None))

    Label_busqueda = tk.Label(ventana, text="Buscar", font=("Arial", 11, "bold"), bg="white")
    entry_busqueda = ttk.Entry(canvas, width=50)


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
               OR CAST(id_proveedor AS CHAR) LIKE %s
        """
        like_termino = f"%{termino}%"
        cursor.execute(consulta, (like_termino, like_termino, like_termino, like_termino, like_termino))
        resultados = cursor.fetchall()
        conexion.close()

        for row in resultados:
            tree.insert("", tk.END, values=row)

    entry_busqueda_var = tk.StringVar()
    entry_busqueda.config(textvariable=entry_busqueda_var)
    entry_busqueda_var.trace("w", buscar_proveedores)  # Búsqueda automática al escribir

    style = ttk.Style()
    style.theme_use("alt")
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"), foreground="white", background="#990000")
    style.map("Treeview.Heading", background=[("!active", "#990000"), ("active", "#990000"), ("pressed", "#990000")],
          foreground=[("!active", "white"), ("active", "white"), ("pressed", "white")])
    
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

    canvas.create_window(550, 380, window=tree, width=1000, height=300)
    tree.place(relx=0.055, rely=0.3, relwidth=0.90, relheight=0.60)
    canvas.create_window(600, 50, window= Label_busqueda)
    Label_busqueda.place(relx=0.28, rely=0.25)
    canvas.create_window(800, 50, window= entry_busqueda)
    entry_busqueda.place(relx=0.35, rely=0.25)
    canvas.create_window(550, 100, window=label_titulo)
    label_titulo.place(relx=0.35, rely=0.10)

    tk.Button(ventana, text="Agregar Proveedor", command=lambda: ventana_agregar_proveedor(tree), font=("Arial", 10,"bold")).place(relx=0.52, rely=0.91, relwidth=0.11, relheight=0.05)
    tk.Button(ventana, text="Modificar Proveedor", command=lambda: ventana_update(tree), font=("Arial", 10,"bold")).place(relx=0.65, rely=0.91, relwidth=0.12, relheight=0.05)
    tk.Button(ventana, text="Eliminar Proveedor", command=lambda: eliminar_proveedor(tree), font=("Arial", 10,"bold")).place(relx=0.78, rely=0.91, relwidth=0.11, relheight=0.05)
    tk.Button(ventana, text="Salir", command= lambda: salir(volver_menu_callback, ventana), bg="red", fg="white", font=("Arial", 10, "bold")).place(relx=0.1, rely=0.92, relwidth=0.08, relheight=0.04)


    cargar_proveedores_tree(tree)
    ventana.mainloop()