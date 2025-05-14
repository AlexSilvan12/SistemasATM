
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from database import conectar_bd
from openpyxl import workbook
from utils import centrar_ventana, ruta_relativa

def obtener_gastos_por_contrato(nombre_contrato=None, mes=None, año=None):
    conexion = conectar_bd()
    cursor = conexion.cursor()

    query = """
        SELECT 
            sp.id_solicitud,
            ac.tipo_solicitud,
            sc.importe,
            sp.fecha_solicitud,
            sp.concepto
        FROM 
            solicitudespago sp
        JOIN 
            autorizacionescompra ac ON sp.id_autorizacion = ac.id_autorizacion
        JOIN 
            solicitud_contratos sc ON sp.id_solicitud = sc.id_solicitud
        JOIN 
            contratos c ON sc.id_contrato = c.id_contrato
        WHERE 
            (%s IS NULL OR c.contrato = %s)
            AND (%s IS NULL OR MONTH(sp.fecha_solicitud) = %s)
            AND (%s IS NULL OR YEAR(sp.fecha_solicitud) = %s)
            AND (sp.estado = 'Autorizado')
    """
    params = (nombre_contrato, nombre_contrato, mes, mes, año, año)
    cursor.execute(query, params)
    datos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return datos

def cargar_contratos(combo):
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT contrato FROM contratos")
    contratos = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conexion.close()

    opciones = ["Todos los contratos"] + contratos
    combo["values"] = opciones
    combo.current(0)

def mostrar_gastos_por_contrato(tree, tree_total, id_contrato=None, mes=None, año=None):
    datos = obtener_gastos_por_contrato(id_contrato, mes, año)

    for item in tree.get_children():
        tree.delete(item)
    for item in tree_total.get_children():
        tree_total.delete(item)

    resumen = {}
    totales_por_tipo = {"Maquinaria": 0, "Equipo y/o Htas": 0, "Servicios": 0, "Otros": 0}

    for id_solicitud, tipo, importe, fecha, concepto in datos:
        if id_solicitud not in resumen:
            resumen[id_solicitud] = {
                "Maquinaria": 0,
                "Equipo y/o Htas": 0,
                "Servicios": 0,
                "Otros": 0,
                "Fecha": fecha,
                "Concepto": concepto
            }
        resumen[id_solicitud][tipo] += importe
        totales_por_tipo[tipo] += importe

    for id_sol, valores in resumen.items():
        tree.insert("", "end", values=(
            id_sol,
            valores["Maquinaria"],
            valores["Equipo y/o Htas"],
            valores["Servicios"],
            valores["Otros"],
            valores["Fecha"],
            valores["Concepto"]
        ))

    total_general = sum(totales_por_tipo.values())

    tree_total.insert("", "end", values=(
        totales_por_tipo["Maquinaria"],
        totales_por_tipo["Equipo y/o Htas"],
        totales_por_tipo["Servicios"],
        totales_por_tipo["Otros"],
        total_general
    ))


def crear_excel():
    wb = workbook()
    sheet = wb.active 

    data = []

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



def costos_contrato():
    ventana = tk.Toplevel()
    ventana.title("Gastos por Contrato")
    centrar_ventana(ventana, 1200, 600)
    
    canvas = tk.Canvas(ventana)
    canvas.pack(fill="both", expand=True)

    def actualizar_degradado(event):
        # Obtener las dimensiones del canvas
        ancho = canvas.winfo_width()
        alto = canvas.winfo_height()
        crear_degradado_vertical(canvas, ancho, alto, "#8B0000", "#FFFFFF")

    # Actualizar el fondo degradado al cambiar el tamaño de la ventana
    canvas.bind("<Configure>", actualizar_degradado)

    # Inicializar el degradado en el tamaño actual de la ventana
    ventana.after(100, lambda: actualizar_degradado(None))

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


    label_titulo = tk.Label(canvas, text="ATM | Costos por Contrato", font=("Arial", 20, "bold"), bg="white")
    label_titulo.place(relx=0.5, rely=0.02, anchor="n")

    # Label y combobox de contrato
    tk.Label(canvas, text="Contrato:", font=("Arial", 10, "bold"), bg="white").place(relx=0.23, rely=0.25)
    combo_contratos = ttk.Combobox(canvas, state="readonly", width=20)
    combo_contratos.place(relx=0.30, rely=0.25)

    # Diccionario de meses
    MESES = {
        "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
        "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
        "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
    }

    # Label y combobox de mes
    tk.Label(canvas, text="Mes:", font=("Arial", 10, "bold"), bg="white").place(relx=0.50, rely=0.2)
    combo_mes = ttk.Combobox(canvas, values=list(MESES.keys()), state="readonly", width=15)
    combo_mes.place(relx=0.55, rely=0.2, relwidth=0.1)

    # Label y combobox de año
    from datetime import datetime
    año_actual = datetime.now().year
    años = [str(a) for a in range(año_actual - 5, año_actual + 2)]

    tk.Label(canvas, text="Año:", font=("Arial", 10, "bold"), bg="white").place(relx=0.50, rely=0.25)
    combo_año = ttk.Combobox(canvas, values=años, state="readonly", width=10)
    combo_año.place(relx=0.55, rely=0.25, relwidth=0.1)

    # Función del botón Filtrar
    def aplicar_filtro():
        nombre_contrato = combo_contratos.get()
        contrato = None if nombre_contrato == "Todos los contratos" else nombre_contrato

        mes_nombre = combo_mes.get()
        mes = MESES.get(mes_nombre)
        año = int(combo_año.get()) if combo_año.get() else None

        mostrar_gastos_por_contrato(tree, tree_total, contrato, mes, año)

    # Botón para aplicar el filtro
    tk.Button(canvas, text="Filtrar", font=("Arial", 10, "bold"), command=aplicar_filtro).place(relx=0.67, rely=0.22)

    # Cargar contratos en el combobox
    cargar_contratos(combo_contratos)
    
    #Estilo de la tabla
    style = ttk.Style()
    style.theme_use("alt")
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"), foreground="white", background="#990000")
    style.map("Treeview.Heading", background=[("!active", "#990000"), ("active", "#990000"), ("pressed", "#990000")],
              foreground=[("!active", "white"), ("active", "white"), ("pressed", "white")])


    tree_frame = ttk.Frame(canvas)
    tree_frame.place(relx=0.025, rely=0.30, relwidth=0.95, relheight=0.5)

    # Identificadores únicos para cada tabla
    columnas_tree = ("Solicitud", "Maquinaria1", "Equipo1", "Servicios1", "Otros1", "Fecha1", "Concepto1")
    tree = ttk.Treeview(tree_frame, columns=columnas_tree, show="headings")

    # Encabezados visibles
    encabezados_visibles = ("Solicitud", "Maquinaria", "Equipo y/o Htas", "Servicios", "Otros", "Fecha de Solicitud", "Concepto")
    for ident, visible in zip(columnas_tree, encabezados_visibles):
        tree.heading(ident, text=visible)
        if ident in ("Solicitud","Maquinaria1", "Equipo1", "Servicios1", "Otros1"):
            tree.column(ident, width=70, anchor="center")
        elif ident == "Fecha1":
            tree.column(ident, width=90, anchor="center")
        else:
            tree.column(ident, width=150, anchor="center")
    tree.pack(fill="both", expand=True)

    # Encabezados específicos solo para el total
    columnas_total = ("Maquinaria", "Equipo y/o Htas", "Servicios", "Otros", "TOTAL")

    tree_total = ttk.Treeview(canvas, columns=columnas_total, show="headings", height=1)
    for col in columnas_total:
        tree_total.heading(col, text=col)
        tree_total.column(col, anchor="center", width=100)

    tree_total.place(relx=0.05, rely=0.83)

    cargar_contratos(combo_contratos)

    def on_seleccion(event):
        nombre_contrato = combo_contratos.get()
        contrato = None if nombre_contrato == "Todos los contratos" else nombre_contrato
        mostrar_gastos_por_contrato(tree, tree_total, contrato)

    combo_contratos.bind("<<ComboboxSelected>>", on_seleccion)
    mostrar_gastos_por_contrato(tree, tree_total, None)
    ventana.mainloop()


if __name__ == "__main__":
    costos_contrato()
