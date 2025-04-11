import tkinter as tk
from tkinter import messagebox
import mysql.connector
from database import conectar_bd
from PIL import Image, ImageTk
import os
import bcrypt
from utils import ruta_relativa, centrar_ventana

def verificar_credenciales(email, password):

    if not email or not password:
        messagebox.showwarning("Campos vacíos", "Por favor, ingresa tus credenciales.")
        return None
        
    conexion = None
    cursor = None

    try:
        # Conectar a la base de datos
        conexion = conectar_bd()
        if conexion is None:
            print("❌ No se pudo establecer la conexión")
            return None
        cursor = conexion.cursor()

        # Obtener la contraseña cifrada de la base de datos
        query = "SELECT password, rol FROM Usuarios WHERE email = %s"
        cursor.execute(query, (email,))
        resultado = cursor.fetchone()

        if resultado:
            contraseña_guardada, rol = resultado
            # Verificar si la contraseña ingresada coincide con la cifrada
            if bcrypt.checkpw(password.encode('utf-8'), contraseña_guardada.encode('utf-8')):
                return rol  # Retorna el rol si la contraseña es correcta

        return None  # Si la contraseña no coincide o el usuario no existe
    
    except mysql.connector.Error as e:
        messagebox.showerror("❌ Error de conexión", f"No se pudo conectar a la base de datos: {e}")

    finally:
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()  

#Funcion para manejar la logica de la GUI
def validar_usuario(entry_email, entry_password, root):

    from main_menu import abrir_menu

    #Recibe los datos desde la intefaz
    email = entry_email.get()
    password = entry_password.get()
    rol = verificar_credenciales(email, password)

    #Condicion para abrir el menú especifico segun el rol
    if rol:
        root.destroy()
        abrir_menu(rol)
    else:
        messagebox.showerror("❌Error", "Credenciales incorrectas")


#GUI
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

def ventana_login():
    ventana = tk.Tk()
    ventana.title("ATM | Gestor de Pagos y Autorizaciones")
    #ventana.geometry("800x600")
    centrar_ventana(ventana, 800, 600)
    canvas = tk.Canvas(ventana, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    RUTA_LOGO = ruta_relativa("Plantillas/LogoATM.png")
    RUTA_LOGO2 = ruta_relativa("Plantillas/ISO-9001.jpeg")
    RUTA_LOGO3 = ruta_relativa("Plantillas/ISO-14001.jpeg")
    RUTA_LOGO4 = ruta_relativa("Plantillas/ISO-45001.jpeg")

    if all(os.path.exists(ruta) for ruta in [RUTA_LOGO, RUTA_LOGO2, RUTA_LOGO3, RUTA_LOGO4]):
        # LOGO ATM
        imagen = Image.open(RUTA_LOGO)
        imagen = imagen.resize((150, 160), Image.Resampling.LANCZOS)
        logo_img = ImageTk.PhotoImage(imagen)
        label_logo = tk.Label(canvas, image=logo_img, borderwidth=0)
        label_logo.image = logo_img
        label_logo.place(relx=0.10, rely=0.01)

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
    else:
        label_logo = tk.Label(canvas, text="LOGO", font=("Arial", 20, "bold"))
        label_logo.place(relx=0.01, rely=0.01)
    

    label_titulo = tk.Label(canvas, text="ATM | Gestor de Pagos y Autorizaciones",
                            font=("Arial", 14, "bold"), fg="black", bg="white")

    label_usuario = tk.Label(canvas, text="Usuario:", font=("Arial", 11, "bold"), bg="white")
    entry_usuario = tk.Entry(canvas, width=30)

    label_contraseña = tk.Label(canvas, text="Contraseña:", font=("Arial", 11, "bold"))
    entry_contraseña = tk.Entry(canvas, show="*", width=30)

    footer = tk.Label(
    canvas,
    text="© Este programa es propiedad de ATM y está prohibida su reproducción no autorizada.",
    font=("Arial", 9, "bold"),
    bg="#990000",  # Fondo blanco, puedes cambiarlo si usas otro color de fondo
    fg="#F2F4F4"   # Color del texto
)
    footer.place(relx=0.5, rely=0.98, anchor="s")


    btn_ingresar = tk.Button(canvas, text="Ingresar", width=20, bg="#283593", fg="white",
                             command=lambda: validar_usuario(entry_usuario, entry_contraseña, ventana))

    btn_salir = tk.Button(canvas, text="Salir", width=15, bg="black", fg="white",
                          font=("Arial", 10, "bold"), command=ventana.destroy)

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

        posiciones_y = {
            'logo': 80,
            'titulo': 200,
            'usuario': 250,
            'entry_usuario': 280,
            'contraseña': 320,
            'entry_contraseña': 350,
            'btn_ingresar': 400,
            'btn_salir': 450,
        }

        for clave, widget_id in widget_ids.items():
            canvas.coords(widget_id, centro_x, posiciones_y[clave])

    def actualizar_canvas_manual():
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        crear_degradado_vertical(canvas, w, h, "#8B0000", "#FFFFFF")
        evento_falso = type('event', (object,), {'width': w, 'height': h})()
        actualizar_canvas(evento_falso)

    canvas.bind("<Configure>", actualizar_canvas)

    ventana.after(100, actualizar_canvas_manual)

    ventana.mainloop()

if __name__ == "__main__":
    ventana_login()