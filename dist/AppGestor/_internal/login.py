import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from database import conectar_bd
from PIL import Image, ImageTk
import os
import bcrypt
from utils import ruta_relativa, centrar_ventana

usuario_actual = {
    "nombre": None,
    "rol": None,
    "firma": None,
    "puesto": None,
    "email": None
}

def verificar_credenciales(email, password):
    if not email or not password:
        messagebox.showwarning("Campos vacíos", "Por favor, ingresa tus credenciales.")
        return None

    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        if conexion is None:
            messagebox.showerror("Error", "No se pudo establecer la conexión con la base de datos.")
            return None

        cursor = conexion.cursor()
        query = "SELECT nombre, password, rol, puesto, ruta_firma FROM Usuarios WHERE email = %s"
        cursor.execute(query, (email,))
        resultado = cursor.fetchone()

        if resultado:
            nombre, contraseña_guardada, rol, puesto, ruta_firma = resultado
            if bcrypt.checkpw(password.encode('utf-8'), contraseña_guardada.encode('utf-8')):
                return {
                    "nombre": nombre,
                    "rol": rol,
                    "firma": ruta_firma,
                    "puesto": puesto
                }

        return None

    except mysql.connector.Error as e:
        messagebox.showerror("❌ Error de conexión", f"No se pudo conectar a la base de datos: {e}")
        return None

    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()


def validar_usuario(entry_email, entry_password, root):
    from main_menu import abrir_menu
    global usuario_actual

    email = entry_email.get()
    password = entry_password.get()
    datos = verificar_credenciales(email, password)

    if datos:
        usuario_actual.update(datos)
        root.destroy()
        abrir_menu(datos["rol"])
    else:
        messagebox.showerror("❌ Error", "Credenciales incorrectas")


def hex_a_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def crear_degradado_vertical(canvas, ancho, alto, color_inicio, color_fin):
    canvas.delete("degradado")
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


def ventana_login():
    ventana = tk.Tk()
    ventana.title("ATM | Gestor de Pagos y Autorizaciones")
    centrar_ventana(ventana, 800, 600)
    canvas = tk.Canvas(ventana, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    rutas = {
        "atm": ruta_relativa("Plantillas/LogoATM.png"),
        "iso1": ruta_relativa("Plantillas/ISO-9001.jpeg"),
        "iso2": ruta_relativa("Plantillas/ISO-14001.jpeg"),
        "iso3": ruta_relativa("Plantillas/ISO-45001.jpeg")
    }

    if all(os.path.exists(ruta) for ruta in rutas.values()):
        logo_img = ImageTk.PhotoImage(Image.open(rutas["atm"]).resize((150, 160), Image.Resampling.LANCZOS))
        iso1_img = ImageTk.PhotoImage(Image.open(rutas["iso1"]).resize((70, 70), Image.Resampling.LANCZOS))
        iso2_img = ImageTk.PhotoImage(Image.open(rutas["iso2"]).resize((70, 70), Image.Resampling.LANCZOS))
        iso3_img = ImageTk.PhotoImage(Image.open(rutas["iso3"]).resize((70, 70), Image.Resampling.LANCZOS))

        label_logo = tk.Label(canvas, image=logo_img, borderwidth=0)
        label_logo.image = logo_img
        label_logo.place(relx=0.10, rely=0.01)

        tk.Label(canvas, image=iso1_img, borderwidth=0, bg="#ffffff").place(relx=0.90, rely=0.01, anchor="ne")
        tk.Label(canvas, image=iso2_img, borderwidth=0, bg="#ffffff").place(relx=0.95, rely=0.15, anchor="ne")
        tk.Label(canvas, image=iso3_img, borderwidth=0, bg="#ffffff").place(relx=0.85, rely=0.15, anchor="ne")
    else:
        label_logo = tk.Label(canvas, text="LOGO", font=("Arial", 20, "bold"))
        label_logo.place(relx=0.01, rely=0.01)

    label_titulo = tk.Label(canvas, text="ATM | Gestor de Pagos y Autorizaciones",
                            font=("Arial", 14, "bold"), fg="black", bg="white")
    label_usuario = tk.Label(canvas, text="Usuario:", font=("Arial", 11, "bold"), bg="white")
    entry_usuario = ttk.Entry(canvas, width=40)
    label_contraseña = tk.Label(canvas, text="Contraseña:", font=("Arial", 11, "bold"), bg="white")
    entry_contraseña = ttk.Entry(canvas, show="*", width=30)

    btn_ingresar = tk.Button(canvas, text="Ingresar", width=20, bg="#283593", fg="white", font=("Arial", 10, "bold"),
                             command=lambda: validar_usuario(entry_usuario, entry_contraseña, ventana))
    btn_salir = tk.Button(canvas, text="Salir", width=15, bg="black", fg="white",
                          font=("Arial", 10, "bold"), command=ventana.destroy)

    footer = tk.Label(canvas, text="© Este programa es propiedad de ATM y está prohibida su reproducción no autorizada.",
                      font=("Arial", 9, "bold"), bg="#990000", fg="#F2F4F4")
    footer.place(relx=0.5, rely=0.98, anchor="s")

    widget_ids = {
        'logo': canvas.create_window(400, 80, window=label_logo),
        'titulo': canvas.create_window(400, 200, window=label_titulo),
        'usuario': canvas.create_window(400, 250, window=label_usuario),
        'entry_usuario': canvas.create_window(400, 280, window=entry_usuario),
        'contraseña': canvas.create_window(400, 320, window=label_contraseña),
        'entry_contraseña': canvas.create_window(400, 350, window=entry_contraseña),
        'btn_ingresar': canvas.create_window(400, 400, window=btn_ingresar),
        'btn_salir': canvas.create_window(400, 450, window=btn_salir),
    }

    def actualizar_canvas(event):
        crear_degradado_vertical(canvas, event.width, event.height, "#8B0000", "#FFFFFF")
        centro_x = event.width // 2
        for clave, widget_id in widget_ids.items():
            canvas.coords(widget_id, centro_x, {
                'logo': 80, 'titulo': 200, 'usuario': 250, 'entry_usuario': 280,
                'contraseña': 320, 'entry_contraseña': 350, 'btn_ingresar': 400, 'btn_salir': 450
            }[clave])

    def actualizar_canvas_manual():
        w, h = canvas.winfo_width(), canvas.winfo_height()
        crear_degradado_vertical(canvas, w, h, "#8B0000", "#FFFFFF")
        evento_falso = type('event', (object,), {'width': w, 'height': h})()
        actualizar_canvas(evento_falso)

    canvas.bind("<Configure>", actualizar_canvas)
    ventana.after(100, actualizar_canvas_manual)
    ventana.mainloop()
