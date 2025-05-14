import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk 
from database import conectar_bd
import mysql.connector
import os
import time
import win32com.client as win32
import pythoncom

def ruta_relativa(ruta_relativa):
    """ Obtiene la ruta correcta del archivo, tanto en desarrollo como en el ejecutable """
    if getattr(sys, 'frozen', False):  # Si el programa está en un .exe
        base_path = sys._MEIPASS  # Carpeta temporal donde PyInstaller extrae los archivos
    else:
        base_path = os.path.abspath(".")  # Carpeta normal si ejecutas el script sin compilar

    return os.path.join(base_path, ruta_relativa)

def centrar_ventana(ventana, ancho, alto):
    # Obtén las dimensiones de la pantalla
    screen_width = ventana.winfo_screenwidth()
    screen_height = ventana.winfo_screenheight()

    # Calcula la posición x, y para centrar la ventana
    pos_x = (screen_width // 2) - (ancho // 2)
    pos_y = (screen_height // 2) - (alto // 2)

    # Establece la geometría de la ventana con la posición calculada
    ventana.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")


def convertir_excel_a_pdf(ruta_excel, ruta_pdf):
    pythoncom.CoInitialize()  # Inicia el hilo COM (recomendado si se llama desde hilos secundarios)
    excel = win32.Dispatch("Excel.Application")
    excel.Visible = False

    try:
        wb = excel.Workbooks.Open(os.path.abspath(ruta_excel))
        hoja = wb.Worksheets(1)

        hoja.PageSetup.Zoom = False
        hoja.PageSetup.FitToPagesWide = 1
        hoja.PageSetup.FitToPagesTall = 1
        hoja.PageSetup.Orientation = 2  # xlLandscape

        hoja.PageSetup.LeftMargin = hoja.PageSetup.Application.InchesToPoints(0.3)
        hoja.PageSetup.RightMargin = hoja.PageSetup.Application.InchesToPoints(0.3)
        hoja.PageSetup.TopMargin = hoja.PageSetup.Application.InchesToPoints(0.5)
        hoja.PageSetup.BottomMargin = hoja.PageSetup.Application.InchesToPoints(0.5)

        time.sleep(1)  # ⚠️ Espera para evitar conflictos de procesos

        wb.ExportAsFixedFormat(0, os.path.abspath(ruta_pdf))  # 0 = PDF
        messagebox.showinfo("✅ Éxito", f"PDF generado: {ruta_pdf}")
        return True

    except Exception as e:
        print(f"❌ Error al convertir a PDF: {e}")
        return False

    finally:
        time.sleep(1)  # ⚠️ Espera antes de cerrar (importante si hay tareas pendientes)
        wb.Close(False)
        excel.Quit()
        pythoncom.CoUninitialize()

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

def cargar_gastos_contrato(tree):
    conexion = conectar_bd()
    cursor = conexion.cursor()

    try:
        consulta = """
        SELECT 
            c.nombre_contrato,
            sp.tipo_solicitud,
            sp.importe_unitario
        FROM solicitudespago sp
        JOIN solicitud_contratos sc ON sp.id_solicitud = sc.id_solicitud
        JOIN contratos c ON sc.id_contrato = c.id_contrato
        WHERE sp.estado = 'Autorizado'
        """
        cursor.execute(consulta)
        resultados = cursor.fetchall()

        # Procesar datos
        gastos = {}
        for contrato, tipo, importe in resultados:
            if contrato not in gastos:
                gastos[contrato] = {
                    "Maquinaria": [],
                    "Equipo y/o Htas": [],
                    "Servicios": [],
                    "Otros": []
                }
            if tipo in gastos[contrato]:
                gastos[contrato][tipo].append(importe)

        # Limpiar tabla
        for item in tree.get_children():
            tree.delete(item)

        # Insertar datos
        for contrato, tipos in gastos.items():
            total = 0
            fila = [contrato]
            for tipo in ["Maquinaria", "Equipo y/o Htas", "Servicios", "Otros"]:
                subtotal = sum(tipos[tipo])
                fila.append(subtotal)
                total += subtotal
            fila.append(total)
            tree.insert("", "end", values=fila)

    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"No se pudo cargar los gastos por contrato: {e}")
    finally:
        cursor.close()
        conexion.close()


def gastos_contrato():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Gastos")
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


    frame_tabla = tk.Frame(canvas)
    frame_tabla.place(relx=0.05, rely=0.28, relwidth=0.9, relheight=0.65)

    columnas = ("Contrato", "Maquinaria", "Equipo y/o Htas", "Servicios", "Otros", "Total")
    tree_gastos = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

    for col in columnas:
        tree_gastos.heading(col, text=col)
        tree_gastos.column(col, anchor="center", width=140 if col == "Contrato" else 120)

    tree_gastos.pack(fill="both", expand=True)

    # Scrollbars
    scrollbar_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree_gastos.yview)
    scrollbar_y.pack(side="right", fill="y")
    tree_gastos.configure(yscrollcommand=scrollbar_y.set)

    scrollbar_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tree_gastos.xview)
    scrollbar_x.pack(side="bottom", fill="x")
    tree_gastos.configure(xscrollcommand=scrollbar_x.set)

    # Cargar datos
    cargar_gastos_contrato(tree_gastos)

    ventana.mainloop()

if __name__ == "__main__":
    gastos_contrato()

