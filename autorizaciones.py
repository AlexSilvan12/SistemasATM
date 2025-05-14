import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from proveedores import cargar_proveedores
from utils import ruta_relativa, centrar_ventana, convertir_excel_a_pdf
from login import usuario_actual
from database import conectar_bd
from openpyxl import load_workbook
from openpyxl.styles import Font
from copy import copy
import os
from openpyxl.styles import Alignment
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.utils import get_column_letter

#Funcion para agregar las autorizaciones
def agregar_autorizacion(entry_consecutivo, combo_tipo, combo_solicitante, entry_puesto, entry_area, entry_fecha_solicitud,
                         entry_fecha_requerida, entry_monto, combo_proveedor, combo_instruccion,
                         entry_flimite, tree, listbox_contratos, entry_IVA, entry_subtotal):
    
    consecutivo = entry_consecutivo.get()
    tipo = combo_tipo.get()
    solicitante = combo_solicitante.get()
    puesto = entry_puesto.get()
    area = entry_area.get()
    fecha_solicitud = entry_fecha_solicitud.get()
    fecha_requerida = entry_fecha_requerida.get()
    monto = entry_monto.get()
    id_proveedor = combo_proveedor.get().split(" - ")[0]
    instruccion = combo_instruccion.get()
    limite = entry_flimite.get()
    seleccionados = listbox_contratos.curselection()
    iva = entry_IVA.get()
    subtotal = entry_subtotal.get()

    if not (tipo and solicitante and puesto and area and fecha_solicitud and fecha_requerida and monto and id_proveedor and instruccion):
        messagebox.showwarning("Campos vacíos", "Por favor, llena todos los campos.")
        return

    if not articulos_lista:
        messagebox.showwarning("Campos vacíos", "Debe agregar al menos un artículo antes de registrar la autorización.")
        return
    
    if not seleccionados:
        messagebox.showwarning("Campos vacíos", "Selecciona al menos un contrato.")
        return    

    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        if conexion is None:
            print("❌No se pudo establecer la conexion")
            return
        cursor = conexion.cursor()

        cursor.execute("SELECT COUNT(*) FROM AutorizacionesCompra WHERE id_autorizacion = %s", (consecutivo,))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Error", f"El ID de autorización '{consecutivo}' ya existe. Elija otro.")
            return

        query = """
        INSERT INTO AutorizacionesCompra 
        (id_autorizacion, tipo_solicitud, solicitante, puesto, area, fecha_solicitud, 
         fecha_requerida, monto, id_proveedor, instruccion, fecha_limite_pago, estado, IVA, subtotal)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pendiente', %s, %s)
        """
        valores = (consecutivo, tipo, solicitante, puesto, area, fecha_solicitud, fecha_requerida,
                  monto, id_proveedor, instruccion, limite, iva, subtotal)
        cursor.execute(query, valores)

        # ✅ Insertar los contratos relacionados
        # Asociar contratos con importes definidos por el usuario
        contratos_ids_nombres = [(listbox_contratos.get(i).split(" - ")[0], listbox_contratos.get(i)) for i in seleccionados]
        importes_contratos = asignar_importes_a_contratos(tree.winfo_toplevel(), contratos_ids_nombres)

        if importes_contratos is None:
            messagebox.showinfo("Cancelado", "Registro de autorización cancelado por el usuario.")
            return  # Detener el guardado

        # Validar que la suma coincida con el monto total ingresado
        suma_importes = sum(importes_contratos.values())
        try:
            monto_float = float(monto)
        except ValueError:
            messagebox.showerror("Error", "El monto total ingresado no es válido.")
            return

        if round(suma_importes, 2) != round(monto_float, 2):
            messagebox.showerror("Error", f"La suma de importes asignados a contratos ({suma_importes}) no coincide con el monto total ({monto_float})")
            return

        # Insertar en tabla con importes asignados
        for id_contrato, importe in importes_contratos.items():
            cursor.execute(
                "INSERT INTO Autorizacion_Contratos (id_autorizacion, id_contrato, importe) VALUES (%s, %s, %s)",
                (consecutivo, id_contrato, importe)
            )

        # ✅ Insertar los artículos relacionados
        query_articulo = """
            INSERT INTO ArticulosAutorizacion (id_autorizacion, cantidad, unidad, articulo, observaciones)
            VALUES (%s, %s, %s, %s, %s)
        """
        for articulo in articulos_lista:
            cursor.execute(query_articulo, (consecutivo, *articulo))

        conexion.commit()
        messagebox.showinfo("✅Éxito", "Autorización y artículos registrados correctamente.")

    except mysql.connector.Error as e:
        if conexion:
            conexion.rollback()
        messagebox.showerror("❌Error", f"Error al agregar autorización: {e}")

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

def cargar_contratos():
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_contrato, contrato FROM contratos")
    contratos = [f"{id} - {nombre}" for id, nombre in cursor.fetchall()]
    cursor.close()
    conexion.close()
    return contratos

def asignar_importes_a_contratos(ventana_padre, contratos_ids_nombres):
    importes = {}
    confirmacion = {"aceptado": False}

    ventana_importes = tk.Toplevel(ventana_padre)
    ventana_importes.title("Asignar importes a contratos")
    centrar_ventana(ventana_importes, 400, 300)
    tk.Label(ventana_importes, text="Asigne el importe a cada contrato", font=("Arial", 12, "bold")).pack(pady=10)

    entries = {}

    for id_contrato, nombre_contrato in contratos_ids_nombres:
        frame = tk.Frame(ventana_importes)
        frame.pack(pady=5)
        tk.Label(frame, text=nombre_contrato).pack(side="left")
        entry = tk.Entry(frame)
        entry.pack(side="left", padx=10)
        entries[id_contrato] = entry

    def confirmar():
        for id_contrato, entry in entries.items():
            valor = entry.get()
            if not valor:
                messagebox.showwarning("Campo vacío", f"Falta el importe del contrato {id_contrato}")
                return
            try:
                importes[id_contrato] = float(valor)
            except ValueError:
                messagebox.showwarning("Error", f"Importe inválido: {valor}")
                return
        confirmacion["aceptado"] = True
        ventana_importes.destroy()

    def cancelar():
        ventana_importes.destroy()

    boton_frame = tk.Frame(ventana_importes)
    boton_frame.pack(pady=10)
    tk.Button(boton_frame, text="Aceptar", command=confirmar, bg="#006600", fg="white").pack(side="left", padx=10)
    tk.Button(boton_frame, text="Cancelar", command=cancelar, bg="red", fg="white").pack(side="left", padx=10)

    ventana_importes.grab_set()
    ventana_padre.wait_window(ventana_importes)

    if confirmacion["aceptado"]:
        return importes
    else:
        return None 


#Funcion para agregar los articulos comprados
articulos_lista = []
def agregar_articulo(entry_cantidad, entry_unidad, entry_articulo, entry_observaciones, tree):
    cantidad = entry_cantidad.get()
    unidad = entry_unidad.get()
    articulo = entry_articulo.get("1.0", "end-1c") 
    observaciones = entry_observaciones.get("1.0", "end-1c")

    if not (cantidad and unidad and articulo):
        messagebox.showwarning("Campos vacíos", "Debe ingresar cantidad, unidad y artículo.")
        return
    
    articulos_lista.append((cantidad, unidad, articulo, observaciones))
    
    tree.insert("", "end", values=(cantidad, unidad, articulo, observaciones))

    # Limpiar campos
    entry_cantidad.delete(0, tk.END)
    entry_unidad.delete(0, tk.END)
    entry_articulo.delete("1.0", "end")
    entry_observaciones.delete("1.0", "end")
        

#Carga las autorizaciones y las muestra en la tabla
def cargar_autorizaciones(tree):

    for row in tree.get_children():
        tree.delete(row)  

        
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
        query = "SELECT id_autorizacion, tipo_solicitud, solicitante, monto, fecha_limite_pago , fecha_solicitud FROM autorizacionescompra"
        cursor.execute(query)
        autorizaciones = cursor.fetchall()

        #Muestra resultados
        for autorizacion in autorizaciones:
            tree.insert("", "end", values=autorizacion)

    except mysql.connector.Error as e:
        print(f"❌Error al cargar autorizaciones: {e}")

    finally:
        #Cierra el cursor y la conexion si fueron creados correctamente
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()


#Carga los articulos y los muestra en la tabla principal
def cargar_articulos(tree):

    for row in tree.get_children():
        tree.delete(row)  

        
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
        query = "SELECT cantidad, unidad, articulo , observaciones FROM articulosautorizacion"
        cursor.execute(query)
        articulos = cursor.fetchall()

        #Muestra resultados
        for articulos in articulos:
            tree.insert("", "end", values=articulos)

    except mysql.connector.Error as e:
        print(f"❌Error al cargar articulos: {e}")

    finally:
        #Cierra el cursor y la conexion si fueron creados correctamente
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()


def limpiar_formulario(entry_consecutivo, combo_tipo, entry_solicitante, entry_puesto, entry_area, entry_fecha_solicitud, 
                       entry_fecha_requerida, entry_monto, combo_proveedor,
                       combo_instruccion, entry_flimite, listbox_contratos, entry_IVA, entry_subtotal):

    entry_consecutivo.delete(0, tk.END)
    combo_tipo.set("")  
    entry_solicitante.delete(0, tk.END)
    entry_puesto.delete(0, tk.END)
    entry_area.delete(0, tk.END)
    entry_fecha_solicitud.delete(0, tk.END)
    entry_fecha_requerida.delete(0, tk.END)
    entry_monto.delete(0, tk.END)
    combo_proveedor.set("")
    combo_instruccion.set("")
    entry_flimite.delete(0, tk.END)
    listbox_contratos.selection_clear(0, tk.END)
    entry_IVA.delete(0, tk.END)
    entry_subtotal.delete(0, tk.END)


#Funcion para limpiar la tabla de articulos
def limpiar_tabla(tree):
    #Elimina todos los registros de la tabla de artículos en la interfaz
    for row in tree.get_children():
        tree.delete(row)
    articulos_lista.clear()


#Funcion para generar el excel
def generar_excel(entry_consecutivo, combo_tipo, combo_solicitante, entry_puesto, entry_area, 
                  entry_fecha_solicitud, entry_fecha_requerida, entry_monto, 
                  combo_proveedor, combo_instruccion, articulos, tree, entry_flimite, listbox_contratos, entry_IVA, entry_subtotal):
    try:
        plantilla_path = ruta_relativa("Plantillas/Autorizaciones.xlsx")
        workbook = load_workbook(plantilla_path)
        sheet = workbook.active

        consecutivo = entry_consecutivo.get()
        tipo_solicitud = combo_tipo.get()
        solicitante = combo_solicitante.get()
        puesto = entry_puesto.get()
        area = entry_area.get()
        fecha_solicitud = entry_fecha_solicitud.get()
        fecha_requerida = entry_fecha_requerida.get()
        monto = entry_monto.get()
        proveedor = combo_proveedor.get()
        instruccion = combo_instruccion.get()

        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT c.contrato
            FROM Autorizacion_Contratos ac
            JOIN contratos c ON ac.id_contrato = c.id_contrato
            WHERE ac.id_autorizacion = %s
        """, (consecutivo,))
        contratos = [row[0] for row in cursor.fetchall()]
        texto_contratos = " / ".join(contratos)
        cursor.close()
        conexion.close()
        
        desplazamiento = max(0, len(articulos) - 10)

        # ✅ Función para escribir y recombinar celdas
        def escribir_celda(fila, columna, valor, rango_combinado=None):
            if rango_combinado:
                sheet.unmerge_cells(rango_combinado)
            celda = sheet.cell(row=fila, column=columna)
            celda.value = valor
            celda.alignment = Alignment(horizontal="center", vertical="center")
            if rango_combinado:
                sheet.merge_cells(rango_combinado)

        # 📝 Escribir datos principales
        escribir_celda(6, 8, consecutivo)
        escribir_celda(12, 2, solicitante, "B12:D12")
        escribir_celda(39, 2, solicitante, "B39:C39")
        escribir_celda(13, 2, puesto, "B13:D13")
        escribir_celda(40, 2, puesto, "B40:C40")
        escribir_celda(14, 2, area, "B14:D14")
        escribir_celda(12, 7, fecha_solicitud, "G12:H12")
        escribir_celda(13, 7, fecha_requerida, "G13:H13")
        escribir_celda(14, 7, texto_contratos, "G14:H14")  # <- contratos aquí
        escribir_celda(32, 2, monto, "B32:H32")
        escribir_celda(31, 2, proveedor, "B31:H31")
        escribir_celda(30, 2, instruccion, "B30:H30")

        # 🧾 Artículos desde fila 17
        fila_inicio = 17
        for i, (cantidad, unidad, articulo, observaciones) in enumerate(articulos):
            escribir_celda(fila_inicio + i, 2, cantidad)      # B
            escribir_celda(fila_inicio + i, 3, unidad)        # C
            escribir_celda(fila_inicio + i, 4, articulo)      # D
            escribir_celda(fila_inicio + i, 7, observaciones) # G

        # Combinar columnas D:F para "artículo"
        col_inicio_art = get_column_letter(4)  # D
        col_fin_art = get_column_letter(6)     # F
        sheet.merge_cells(f"{col_inicio_art}{fila_inicio}:{col_fin_art}{fila_inicio}")

        # Combinar columnas G:H para "observaciones"
        col_inicio_obs = get_column_letter(7)  # G
        col_fin_obs = get_column_letter(8)     # H
        sheet.merge_cells(f"{col_inicio_obs}{fila_inicio}:{col_fin_obs}{fila_inicio}")

        # ✅ Tipo de solicitud con marca "X"
        tipo_a_celda = {
            "Maquinaria": "B10",
            "Equipo y/o Htas": "D10",
            "Servicios": "F10",
            "Otros": "H10"
        }

        # Limpiar anteriores
        for celda in tipo_a_celda.values():
            sheet[celda].value = ""

        if tipo_solicitud in tipo_a_celda:
            celda_obj = sheet[tipo_a_celda[tipo_solicitud]]
            celda_obj.value = "X"
            celda_obj.font = Font(bold=True, color="FF0000")

        # Firma
        ruta_firma = ruta_relativa(usuario_actual["firma"])
        firma_img = ExcelImage(ruta_firma)
        firma_img.width = 120
        firma_img.height = 50
        sheet.add_image(firma_img, "B37")

        # Firma
        ruta_firma = ruta_relativa(usuario_actual["firma"])
        firma_img = ExcelImage(ruta_firma)
        firma_img.width = 120
        firma_img.height = 50
        fila_firma = 37 + desplazamiento
        sheet.add_image(firma_img, f"B{fila_firma}")


        # 📁 Guardar archivo Excel
        CARPETA_AUTORIZACIONES = ruta_relativa("Autorizaciones")
        output_path = os.path.join(CARPETA_AUTORIZACIONES, f"Autorizacion_{consecutivo}.xlsx")
        workbook.save(output_path)

        # 📄 Convertir a PDF
        ruta_pdf = output_path.replace(".xlsx", ".pdf")
        convertir_excel_a_pdf(output_path, ruta_pdf)
        os.startfile(ruta_pdf)

        # 🧹 Limpiar y recargar
        limpiar_formulario(entry_consecutivo, combo_tipo, combo_solicitante, entry_puesto, entry_area, 
                           entry_fecha_solicitud, entry_fecha_requerida, entry_monto, 
                           combo_proveedor, combo_instruccion, entry_flimite, listbox_contratos, entry_IVA, entry_subtotal)
        cargar_autorizaciones(tree)
        articulos_lista.clear()
        limpiar_tabla(tree)
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el archivo Excel: {e}")
        return


#Interfaz de Usuario
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


def gestionar_autorizaciones():

    def filtrar_proveedores(event):
        texto = combo_proveedor.get().lower()  # Obtener el texto en minúsculas
        combo_proveedor["values"] = [prov for prov in proveedores if texto in prov.lower()]  # Filtrar proveedores

        # Mover el cursor al final del texto para evitar que se resetee la posición
        combo_proveedor.icursor(tk.END)  

    ventana = tk.Toplevel()
    ventana.title("Gestión de Autorizaciones de Compra")
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


    # Función para calcular posiciones relativas
    def pos(x, y):
        return {"relx": x, "rely": y, "anchor": "w"}   
    
    #Etiqueta de instruccion
    tk.Label(ventana, text="Datos Generales de la Autorizacion de Compra", font=("Arial", 12, "bold"), bg="white").place(**pos(0.07, 0.03))
    
    tk.Label(ventana, text="Consecutivo: ", font=("Arial", 10, "bold"), bg="white").place(**pos(0.05, 0.10))
    entry_consecutivo = ttk.Entry(ventana)
    entry_consecutivo.place(**pos(0.3, 0.10))


    tk.Label(ventana, text="Tipo de Solicitud: ", font=("Arial", 10, "bold"), bg="white").place(**pos(0.05, 0.15))
    combo_tipo = ttk.Combobox(ventana, values=["Maquinaria", "Equipo y/o Htas", "Servicios", "Otros"])
    combo_tipo.place(**pos(0.3, 0.15))

    
    tk.Label(ventana, text="Solicitante:", font=("Arial", 10, "bold"), bg="white").place(**pos(0.05, 0.20))
    entry_solicitante = ttk.Entry(ventana, state="readonly")
    entry_solicitante.place(**pos(0.3, 0.20), relwidth=0.20)
    entry_solicitante.config(state="normal")
    entry_solicitante.insert(0, usuario_actual["nombre"])
    entry_solicitante.config(state="readonly")

    tk.Label(ventana, text="Puesto:", font=("Arial", 10, "bold"), bg="white").place(**pos(0.05, 0.25))
    entry_puesto = ttk.Entry(ventana, state="readonly")
    entry_puesto.place(**pos(0.3, 0.25), relwidth=0.20)
    entry_puesto.config(state="normal")
    entry_puesto.insert(0, usuario_actual["puesto"])
    entry_puesto.config(state="readonly")

    tk.Label(ventana, text="Área:", font=("Arial", 10, "bold"), bg="white").place(**pos(0.05, 0.30))
    entry_area = ttk.Entry(ventana)
    entry_area.place(**pos(0.3, 0.30))

    tk.Label(ventana, text="Fecha de Solicitud (AAAA/MM/DD):", font=("Arial", 10, "bold"), bg="white").place(**pos(0.05, 0.35))
    entry_fecha_solicitud = ttk.Entry(ventana)
    entry_fecha_solicitud.place(**pos(0.3, 0.35))

    tk.Label(ventana, text="Fecha Requerida (AAAA/MM/DD):", font=("Arial", 10, "bold"), bg="white").place(**pos(0.05, 0.40))
    entry_fecha_requerida = ttk.Entry(ventana)
    entry_fecha_requerida.place(**pos(0.3, 0.40))

    tk.Label(ventana, text="Proyecto(s) / Contrato(s):", font=("Arial", 10, "bold"), bg="white").place(**pos(0.05, 0.5))
    frame_contratos = ttk.Frame(ventana, relief="solid", borderwidth=1)
    frame_contratos.place(**pos(0.3, 0.5), relwidth=0.2, relheight=0.15)
    scrollbar_y = ttk.Scrollbar(frame_contratos, orient="vertical")
    scrollbar_y.pack(side="right", fill="y")
    listbox_contratos = tk.Listbox(frame_contratos, selectmode="multiple", height=5, font=("Arial", 10),
                                yscrollcommand=scrollbar_y.set, exportselection=False)
    listbox_contratos.pack(side="left", fill="both", expand=True)

    scrollbar_y.config(command=listbox_contratos.yview)

    for contrato in cargar_contratos():
        listbox_contratos.insert(tk.END, contrato)

    tk.Label(ventana, text="Limite de Pago:", font=("Arial", 10, "bold"), bg="#ffebeb").place(**pos(0.05, 0.60))
    entry_flimite = ttk.Entry(ventana)
    entry_flimite.place(**pos(0.3, 0.60))

    tk.Label(ventana, text="Proveedor:", font=("Arial", 10, "bold"), bg="#ffebeb").place(**pos(0.05, 0.65))
    proveedores = cargar_proveedores()
    combo_proveedor = ttk.Combobox(ventana, values=proveedores)
    combo_proveedor.place(**pos(0.3, 0.65), relwidth=0.20)
    combo_proveedor.bind("<KeyRelease>", filtrar_proveedores)  # Llamar a la función al escribir

    #Etiqueta de instruccion de llenado de articulos
    tk.Label(ventana, text="Ingrese los datos de la compra", font=("Arial", 12, "bold"), bg="white").place(**pos(0.57, 0.03))

    tk.Label(ventana, text="Cantidad:", font=("Arial", 10, "bold"), bg="white").place(**pos(0.55, 0.10))
    entry_cantidad = ttk.Entry(ventana)
    entry_cantidad.place(**pos(0.75, 0.10))

    tk.Label(ventana, text="Unidad:", font=("Arial", 10, "bold"), bg="white").place(**pos(0.55, 0.15))
    entry_unidad = ttk.Entry(ventana)
    entry_unidad.place(**pos(0.75, 0.15))

    tk.Label(ventana, text="Descripción:", font=("Arial", 10, "bold"), bg="white").place(**pos(0.55, 0.20))
    entry_articulo = tk.Text(ventana, wrap="word", font=("Arial", 11))
    entry_articulo.place(relx=0.55, rely=0.23, relwidth=0.38, relheight=0.08)  # Más espacio vertical y horizontal

    tk.Label(ventana, text="Observaciones:", font=("Arial", 10, "bold"), bg="white").place(**pos(0.55, 0.33))
    entry_observaciones = tk.Text(ventana, wrap="word", font=("Arial", 11))
    entry_observaciones.place(relx=0.55, rely=0.36, relwidth=0.38, relheight=0.08)

    tk.Label(ventana, text="Subtotal: ", font=("Arial", 10, "bold"), bg="#ffebeb").place(**pos(0.55, 0.60))
    entry_subtotal = ttk.Entry(ventana)
    entry_subtotal.place(**pos(0.63, 0.60))

    tk.Label(ventana, text="IVA: ", font=("Arial", 10, "bold"), bg="#ffebeb").place(**pos(0.55, 0.65))
    entry_IVA = ttk.Entry(ventana)
    entry_IVA.place(**pos(0.60, 0.65))

    tk.Label(ventana, text="Monto Total: ", font=("Arial", 10, "bold"), bg="#ffebeb").place(**pos(0.75, 0.60))
    entry_monto = ttk.Entry(ventana)
    entry_monto.place(**pos(0.85, 0.60))

    tk.Label(ventana, text="Forma de Pago: ", font=("Arial", 10, "bold"), bg="#ffebeb").place(**pos(0.75, 0.65))
    combo_instruccion = ttk.Combobox(ventana, values=["Transferencia Electrónica", "Tarjeta de Débito", "Efectivo"])
    combo_instruccion.place(**pos(0.85, 0.65))


    style = ttk.Style()
    style.theme_use("alt")
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"), foreground="white", background="#990000")
    style.map("Treeview.Heading", background=[("!active", "#990000"), ("active", "#990000"), ("pressed", "#990000")],
          foreground=[("!active", "white"), ("active", "white"), ("pressed", "white")]) 

    # Tabla de artículos
    tree = ttk.Treeview(ventana, columns=("Cantidad", "Unidad", "Descripción", "Observaciones"), show="headings")
    tree.heading("Cantidad", text="Cantidad")
    tree.heading("Unidad", text="Unidad")
    tree.heading("Descripción", text="Descripción")
    tree.heading("Observaciones", text="Observaciones")
    tree.place(relx=0.05, rely=0.70, relwidth=0.9, relheight=0.2)  # Tamaño relativo

    #Ventana para vizualizar las autorizaciones cargadas
    def autorizaciones(tree):
    
        ventana = tk.Toplevel()
        ventana.title("Autorizaciones Guardadas")
        centrar_ventana(ventana, 1300, 600)

        style = ttk.Style()
        style.theme_use("alt")
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), foreground="white", background="#990000")
        style.map("Treeview.Heading", background=[("!active", "#990000"), ("active", "#990000"), ("pressed", "#990000")],
            foreground=[("!active", "white"), ("active", "white"), ("pressed", "white")])

        tree = ttk.Treeview(ventana, columns=("ID","Tipo", "Solicitante", "Monto", "Fecha Limite","Fecha solicitud"), show="headings")
        for col in ("ID","Tipo", "Solicitante", "Monto", "Fecha Limite","Fecha solicitud"):
            tree.heading(col, text=col)
        tree.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.8)
        cargar_autorizaciones(tree)
        tk.Button(ventana, text="Salir", command= ventana.destroy, bg="red", fg="white", font=("Arial", 10, "bold")).place(relx=0.05, rely=0.91, relwidth=0.095, relheight=0.05)


    
    tk.Button(ventana, text="Agregar Artículo", command=lambda: agregar_articulo(entry_cantidad, entry_unidad, entry_articulo, entry_observaciones, tree), foreground="white", background="#990000", font=("Arial", 10, "bold")).place(relx=0.75, rely=0.50, relwidth=0.095, relheight=0.05)


    tk.Button(ventana, text="Registrar Autorización", command=lambda: agregar_autorizacion(entry_consecutivo,
        combo_tipo, entry_solicitante, entry_puesto, entry_area, entry_fecha_solicitud, 
        entry_fecha_requerida, entry_monto, combo_proveedor, combo_instruccion, entry_flimite, tree, listbox_contratos, entry_IVA, entry_subtotal), font=("Arial", 10, "bold")).place(relx=0.48, rely=0.91, relwidth=0.15, relheight=0.05)

    tk.Button(ventana, text="Generar Docs", command=lambda: generar_excel(entry_consecutivo,
        combo_tipo, entry_solicitante, entry_puesto, entry_area, entry_fecha_solicitud, 
        entry_fecha_requerida, entry_monto, combo_proveedor, combo_instruccion, articulos_lista, tree, entry_flimite, listbox_contratos, entry_IVA, entry_subtotal), font=("Arial", 10, "bold")).place(relx=0.65, rely=0.91, relwidth=0.095, relheight=0.05)
    
    tk.Button(ventana,text="Autorizaciones Guardadas", command=lambda: autorizaciones(tree), font=("Arial", 10, "bold")).place(relx=0.78, rely=0.91, relwidth=0.15, relheight=0.05)

    tk.Button(ventana, text="Salir", command= ventana.destroy, bg="red", fg="white", font=("Arial", 10, "bold")).place(relx=0.05, rely=0.91, relwidth=0.095, relheight=0.05)


    ventana.mainloop()
    
if __name__ == "__main__":
    gestionar_autorizaciones()