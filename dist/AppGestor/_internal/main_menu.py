import tkinter as tk
from PIL import Image, ImageTk
from proveedores import gestionar_proveedores
from solicitudes import gestionar_solicitudes
from autorizaciones import gestionar_autorizaciones
from usuarios import gestionar_usuarios
from gerente import Autorizacion_Pagos_Compras
from utils import ruta_relativa, centrar_ventana
import importlib

LOGO_PATH = ruta_relativa("Plantillas/LogoATM.png")
RUTA_LOGO2 = ruta_relativa("Plantillas/ISO-9001.jpeg")
RUTA_LOGO3 = ruta_relativa("Plantillas/ISO-14001.jpeg")
RUTA_LOGO4 = ruta_relativa("Plantillas/ISO-45001.jpeg")

def cerrar_sesion(ventana):
    ventana.destroy()
    importlib.import_module("login").ventana_login()

def hex_a_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2 ,4))

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

def abrir_menu(rol):
    root = tk.Tk()
    centrar_ventana(root, 800, 600)
    root.title(f"Menú {rol}")

    canvas = tk.Canvas(root, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    widgets = {}

    try:
        imagen = Image.open(LOGO_PATH).resize((150, 160), Image.Resampling.LANCZOS)
        logo_img = ImageTk.PhotoImage(imagen)
        label_logo = tk.Label(canvas, image=logo_img, borderwidth=0)
        label_logo.image = logo_img
        widgets['logo'] = canvas.create_window(400, 100, window=label_logo)

        iso1 = Image.open(RUTA_LOGO2).resize((70, 70), Image.Resampling.LANCZOS)
        iso1_img = ImageTk.PhotoImage(iso1)
        label_iso1 = tk.Label(canvas, image=iso1_img, borderwidth=0, bg="#ffffff")
        label_iso1.image = iso1_img
        label_iso1.place(relx=0.90, rely=0.01, anchor="ne")

        iso2 = Image.open(RUTA_LOGO3).resize((70, 70), Image.Resampling.LANCZOS)
        iso2_img = ImageTk.PhotoImage(iso2)
        label_iso2 = tk.Label(canvas, image=iso2_img, borderwidth=0, bg="#ffffff")
        label_iso2.image = iso2_img
        label_iso2.place(relx=0.95, rely=0.15, anchor="ne")

        iso3 = Image.open(RUTA_LOGO4).resize((70, 70), Image.Resampling.LANCZOS)
        iso3_img = ImageTk.PhotoImage(iso3)
        label_iso3 = tk.Label(canvas, image=iso3_img, borderwidth=0, bg="#ffffff")
        label_iso3.image = iso3_img
        label_iso3.place(relx=0.85, rely=0.15, anchor="ne")

    except Exception as e:
        print(f"⚠️ No se pudo cargar una o más imágenes: {e}")
        label_logo = tk.Label(canvas, text="LOGO", font=("Arial", 20, "bold"))
        widgets['logo'] = canvas.create_window(400, 100, window=label_logo)

    # ✅ Función para cerrar menú y abrir el módulo correspondiente
    def abrir_modulo(funcion_modulo):
        root.destroy()
        funcion_modulo(rol, lambda: abrir_menu(rol))

    botones = []
    if rol == "Administrador":
        botones = [
            ("Gestión de Usuarios", gestionar_usuarios),
            ("Gestión de Proveedores", gestionar_proveedores),
            ("Gestión de Autorizaciones", gestionar_autorizaciones),
            ("Gestión de Solicitudes", gestionar_solicitudes)
        ]
    elif rol == "Contador":
        botones = [
            ("Gestión de Autorizaciones", gestionar_autorizaciones),
            ("Gestión de Solicitudes", gestionar_solicitudes),
            ("Gestión de Proveedores", gestionar_proveedores)
        ]
    elif rol == "Comprador":
        botones = [
            ("Gestión de Autorizaciones", gestionar_autorizaciones),
            ("Gestión de Solicitudes", gestionar_solicitudes),
            ("Gestión de Proveedores", gestionar_proveedores)
        ]
    elif rol == "Gerente":
        botones = [
            ("Gestión de Autorizaciones", gestionar_autorizaciones),
            ("Gestión de Solicitudes", gestionar_solicitudes),
            ("Gestión de Proveedores", gestionar_proveedores),
            ("Autorizaciones de Compra y Solicitudes de Pago por Autorizar", Autorizacion_Pagos_Compras)
        ]

    y_base = 240
    for i, (texto, funcion) in enumerate(botones):
        ancho = 50 if texto.startswith("Autorizaciones") else 30
        btn = tk.Button(
            canvas, text=texto, width=ancho, height=2, font=("Arial", 10, "bold"),
            command=lambda f=funcion: abrir_modulo(f)
        )
        widgets[f"btn_{i}"] = canvas.create_window(400, y_base + i * 60, window=btn)

    btn_cerrar = tk.Button(
        canvas, text="Cerrar sesión", width=15, bg="#cc0000", fg="white",
        font=("Arial", 10, "bold"), command=lambda: cerrar_sesion(root)
    )
    widgets['cerrar'] = canvas.create_window(400, y_base + len(botones) * 60 + 30, window=btn_cerrar)

    def actualizar_canvas(event):
        crear_degradado_vertical(canvas, event.width, event.height, "#8B0000", "#FFFFFF")
        centro_x = event.width // 2
        for clave, widget_id in widgets.items():
            coords = canvas.coords(widget_id)
            if coords:
                y = coords[1]
                canvas.coords(widget_id, centro_x, y)

    def actualizar_canvas_manual():
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        crear_degradado_vertical(canvas, w, h, "#8B0000", "#FFFFFF")
        evento_falso = type('event', (object,), {'width': w, 'height': h})()
        actualizar_canvas(evento_falso)

    canvas.bind("<Configure>", actualizar_canvas)
    root.after(100, actualizar_canvas_manual)

    root.mainloop()