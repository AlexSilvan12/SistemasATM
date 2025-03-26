import tkinter as tk
from PIL import Image, ImageTk
import os
import login  # Para volver al login al cerrar sesión

# Ruta del logotipo
LOGO_PATH = os.path.join("plantillas", "LogoATM.png")

# Función para cerrar sesión y volver al login
def cerrar_sesion(ventana):
    ventana.destroy()
    login.ventana_login()

# Ventana del menú principal
def mostrar_menu_principal():
    ventana = tk.Tk()
    ventana.title("ATM | Gestor de Pagos y Autorizaciones")
    ventana.geometry("800x600")
    ventana.configure(bg="white")

    # Cargar logotipo
    try:
        imagen = Image.open(LOGO_PATH)
        imagen = imagen.resize((120, 120), Image.Resampling.LANCZOS)
        logo = ImageTk.PhotoImage(imagen)
        logo_label = tk.Label(ventana, image=logo, bg="white")
        logo_label.image = logo
        logo_label.pack(pady=10)
    except Exception as e:
        print(f"⚠️ No se pudo cargar el logotipo: {e}")

    # Título de la app
    tk.Label(ventana, text="ATM | Gestor de Pagos y Autorizaciones",
             font=("Arial", 20, "bold"), bg="white", fg="#003366").pack(pady=10)

    # Área de botones principales
    frame_botones = tk.Frame(ventana, bg="white")
    frame_botones.pack(pady=20)

    # Aquí puedes agregar botones funcionales del sistema
    tk.Button(frame_botones, text="Gestión de Autorizaciones", width=30, height=2).grid(row=0, column=0, padx=10, pady=10)
    tk.Button(frame_botones, text="Solicitudes de Pago", width=30, height=2).grid(row=0, column=1, padx=10, pady=10)

    # Botón para cerrar sesión
    tk.Button(ventana, text="Cerrar sesión", command=lambda: cerrar_sesion(ventana),
              bg="#cc0000", fg="white", font=("Arial", 10, "bold"), width=15).pack(pady=20)

    ventana.mainloop()

# Para pruebas locales
if __name__ == "__main__":
    mostrar_menu_principal()
