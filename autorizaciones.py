import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from proveedores import cargar_proveedores
from usuarios import cargar_usuarios
from database import conectar_bd
from openpyxl import load_workbook
from openpyxl.styles import Font
import os
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter

#Funcion para agregar las autorizaciones
def agregar_autorizacion(entry_consecutivo, combo_tipo, combo_solicitante, entry_puesto, entry_area, entry_fecha_solicitud, entry_fecha_requerida, entry_proyecto, entry_monto, combo_proveedor, combo_instruccion, entry_flimite, tree):
    consecutivo = entry_consecutivo.get()
    tipo = combo_tipo.get()
    solicitante = combo_solicitante.get()
    puesto = entry_puesto.get()
    area = entry_area.get()
    fecha_solicitud = entry_fecha_solicitud.get()
    fecha_requerida = entry_fecha_requerida.get()
    proyecto_contrato = entry_proyecto.get()
    monto = entry_monto.get()
    id_proveedor = combo_proveedor.get().split(" - ")[0]
    instruccion = combo_instruccion.get()
    limite = entry_flimite.get()


    if not (tipo and solicitante and puesto and area and fecha_solicitud and fecha_requerida and proyecto_contrato and monto and id_proveedor and instruccion):
        messagebox.showwarning("Campos vacíos", "Por favor, llena todos los campos.")
        return
    
    if not articulos_lista:
        messagebox.showwarning("Advertencia", "Debe agregar al menos un artículo antes de registrar la autorización.")
        return
        
    #Inicializamos conexion y cursor
    conexion = None
    cursor =  None

    try:
        #Conexion a la base de datos
        conexion = conectar_bd()
        if conexion is None:
            print ("❌No se pudo establecer la conexion")
        cursor = conexion.cursor()

        #Verifica si el ID de autorizacion ya existe
        cursor.execute("SELECT COUNT(*) FROM AutorizacionesCompra WHERE id_autorizacion = %s", (consecutivo,))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Error", f"El ID de autorización '{consecutivo}' ya existe. Elija otro.")
            return

        #Ejecuta la consulta para insertar la autorizacion
        query = """
        INSERT INTO AutorizacionesCompra (id_autorizacion, tipo_solicitud, solicitante, puesto, area, fecha_solicitud, fecha_requerida, proyecto_contrato, monto, id_proveedor, instruccion, fecha_limite_pago)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        

        valores = (consecutivo, tipo, solicitante, puesto, area, fecha_solicitud, fecha_requerida, proyecto_contrato, monto, id_proveedor, instruccion, limite)
        cursor.execute(query, valores)
        

        #Ejecuta la consulta para insertar los articulos relacionados
        query_articulo = """
            INSERT INTO ArticulosAutorizacion (id_autorizacion, cantidad, unidad, articulo, observaciones)
            VALUES (%s, %s, %s, %s, %s)
        """ 
        
        for articulo in articulos_lista:
            cursor.execute(query_articulo, (consecutivo, *articulo))

        conexion.commit()

        #Muestra resultado
        messagebox.showinfo("✅Éxito", "Autorización y articulos registrados correctamente.")
        

    except mysql.connector.Error as e:
        conexion.rollback()
        messagebox.showerror("❌Error", f"Error al agregar autorizacion: {e}")    

    finally:
        #Cierra el cursor y la conexion si fueron creados correctamente
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()


#Funcion para agregar los articulos comprados
articulos_lista = []
def agregar_articulo(entry_cantidad, entry_unidad, entry_articulo, entry_observaciones, tree):
    cantidad = entry_cantidad.get()
    unidad = entry_unidad.get()
    articulo = entry_articulo.get()
    observaciones = entry_observaciones.get()

    if not (cantidad and unidad and articulo):
        messagebox.showwarning("Campos vacíos", "Debe ingresar cantidad, unidad y artículo.")
        return
    
    articulos_lista.append((cantidad, unidad, articulo, observaciones))
    
    tree.insert("", "end", values=(cantidad, unidad, articulo, observaciones))

    # Limpiar campos
    entry_cantidad.delete(0, tk.END)
    entry_unidad.delete(0, tk.END)
    entry_articulo.delete(0, tk.END)
    entry_observaciones.delete(0, tk.END)
        

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


def limpiar_formulario(entry_consecutivo, combo_tipo, combo_solicitante, entry_puesto, entry_area, entry_fecha_solicitud, 
                       entry_fecha_requerida, entry_proyecto, entry_monto, combo_proveedor,
                        combo_instruccion, entry_flimite):
    
    entry_consecutivo.delete(0, tk.END)
    combo_tipo.set("")  
    combo_solicitante.set("")
    entry_puesto.delete(0, tk.END)
    entry_area.delete(0, tk.END)
    entry_fecha_solicitud.delete(0, tk.END)
    entry_fecha_requerida.delete(0, tk.END)
    entry_proyecto.delete(0, tk.END)
    entry_monto.delete(0, tk.END)
    combo_proveedor.set("")
    combo_instruccion.set("")
    entry_flimite.delete(0, tk.END)

#Funcion para limpiar la tabla de articulos
def limpiar_tabla(tree):
    #Elimina todos los registros de la tabla de artículos en la interfaz
    for row in tree.get_children():
        tree.delete(row)
    articulos_lista.clear()


#Funcion para generar el excel
def generar_excel(entry_consecutivo, combo_tipo, combo_solicitante, entry_puesto, entry_area, 
                  entry_fecha_solicitud, entry_fecha_requerida, entry_proyecto, entry_monto, 
                  combo_proveedor, combo_instruccion, articulos, tree, entry_flimite):
    
    try:
        plantilla_path = "Plantillas\\Autorizaciones.xlsx"
        workbook = load_workbook(plantilla_path)
        sheet = workbook.active

        consecutivo = entry_consecutivo.get()
        tipo_solicitud = combo_tipo.get()
        solicitante = combo_solicitante.get()
        puesto = entry_puesto.get()
        area = entry_area.get()
        fecha_solicitud = entry_fecha_solicitud.get()
        fecha_requerida = entry_fecha_requerida.get()
        proyecto_contrato = entry_proyecto.get()
        monto = entry_monto.get()
        proveedor = combo_proveedor.get()
        instruccion = combo_instruccion.get()


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
        escribir_celda(14, 7, proyecto_contrato, "G14:H14")
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
            "Otros": "H9"
        }

        # Limpiar anteriores
        for celda in tipo_a_celda.values():
            sheet[celda].value = ""

        if tipo_solicitud in tipo_a_celda:
            celda_obj = sheet[tipo_a_celda[tipo_solicitud]]
            celda_obj.value = "X"
            celda_obj.font = Font(bold=True, color="FF0000")

        # 📁 Guardar y abrir archivo
        output_path = "Autorizaciones\\Autorizacion_{consecutivo}.xlsx"
        workbook.save(output_path)
        os.startfile(output_path)

        # 🧹 Limpiar y recargar
        limpiar_formulario(entry_consecutivo, combo_tipo, combo_solicitante, entry_puesto, entry_area, 
                           entry_fecha_solicitud, entry_fecha_requerida, entry_proyecto, entry_monto, 
                           combo_proveedor, combo_instruccion, entry_flimite)
        cargar_autorizaciones(tree)
        articulos_lista.clear()
        limpiar_tabla(tree)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el archivo Excel: {e}")


#Interfaz de Usuario
def gestionar_autorizaciones():

    def filtrar_proveedores(event):
        texto = combo_proveedor.get().lower()  # Obtener el texto en minúsculas
        combo_proveedor["values"] = [prov for prov in proveedores if texto in prov.lower()]  # Filtrar proveedores

        # Mover el cursor al final del texto para evitar que se resetee la posición
        combo_proveedor.icursor(tk.END)  

    ventana = tk.Tk()
    ventana.title("Gestión de Autorizaciones de Compra")
    ventana.geometry("1200x600")

    # Función para calcular posiciones relativas
    def pos(x, y):
        return {"relx": x, "rely": y, "anchor": "w"}  # Posiciona desde la izquierda
    
    tk.Label(ventana, text="Consecutivo: ").place(**pos(0.05, 0.05))
    entry_consecutivo = tk.Entry(ventana)
    entry_consecutivo.place(**pos(0.3, 0.05))


    tk.Label(ventana, text="Tipo de Solicitud: ").place(**pos(0.05, 0.10))
    combo_tipo = ttk.Combobox(ventana, values=["Maquinaria", "Equipo y/o Htas", "Servicios", "Otros"])
    combo_tipo.place(**pos(0.3, 0.10))

    tk.Label(ventana, text="Solicitante:").place(**pos(0.05, 0.15))
    solicitante = cargar_usuarios()
    combo_solicitante = ttk.Combobox(ventana, values=solicitante)
    combo_solicitante.place(**pos(0.3, 0.15))

    tk.Label(ventana, text="Puesto:").place(**pos(0.05, 0.20))
    entry_puesto = tk.Entry(ventana)
    entry_puesto.place(**pos(0.3, 0.20))

    tk.Label(ventana, text="Área:").place(**pos(0.05, 0.25))
    entry_area = tk.Entry(ventana)
    entry_area.place(**pos(0.3, 0.25))

    tk.Label(ventana, text="Fecha de Solicitud (AAAA/MM/DD):").place(**pos(0.05, 0.30))
    entry_fecha_solicitud = tk.Entry(ventana)
    entry_fecha_solicitud.place(**pos(0.3, 0.30))

    tk.Label(ventana, text="Fecha Requerida (AAAA/MM/DD):").place(**pos(0.05, 0.35))
    entry_fecha_requerida = tk.Entry(ventana)
    entry_fecha_requerida.place(**pos(0.3, 0.35))

    tk.Label(ventana, text="Proyecto y/o contrato:").place(**pos(0.05, 0.40))
    entry_proyecto = tk.Entry(ventana)
    entry_proyecto.place(**pos(0.3, 0.40))

    tk.Label(ventana, text="Monto Total (solo valor numérico):").place(**pos(0.05, 0.45))
    entry_monto = tk.Entry(ventana)
    entry_monto.place(**pos(0.3, 0.45))

    tk.Label(ventana, text="Proveedor:").place(**pos(0.05, 0.50))
    proveedores = cargar_proveedores()
    combo_proveedor = ttk.Combobox(ventana, values=proveedores)
    combo_proveedor.place(relx=0.3, rely=0.50)
    combo_proveedor.bind("<KeyRelease>", filtrar_proveedores)  # Llamar a la función al escribir


    tk.Label(ventana, text="Cantidad:").place(**pos(0.55, 0.05))
    entry_cantidad = tk.Entry(ventana)
    entry_cantidad.place(**pos(0.75, 0.05))

    tk.Label(ventana, text="Unidad:").place(**pos(0.55, 0.10))
    entry_unidad = ttk.Entry(ventana)
    entry_unidad.place(**pos(0.75, 0.10))

    tk.Label(ventana, text="Descripción:").place(**pos(0.55, 0.15))
    entry_articulo = tk.Entry(ventana)
    entry_articulo.place(**pos(0.75, 0.15))

    tk.Label(ventana, text="Observaciones:").place(**pos(0.55, 0.20))
    entry_observaciones = tk.Entry(ventana)
    entry_observaciones.place(**pos(0.75, 0.20))

    tk.Label(ventana, text="Instrucción: ").place(**pos(0.55, 0.25))
    combo_instruccion = ttk.Combobox(ventana, values=["Transferencia Electrónica", "Tarjeta de Débito", "Efectivo"])
    combo_instruccion.place(**pos(0.75, 0.25))

    tk.Label(ventana, text="Limite de Pago: ").place(**pos(0.55, 0.30))
    entry_flimite = ttk.Entry(ventana)
    entry_flimite.place(**pos(0.75, 0.30))

    # Tabla de artículos
    tk.Label(ventana, text="Artículos:").place(**pos(0.05, 0.55))
    tree = ttk.Treeview(ventana, columns=("Cantidad", "Unidad", "Descripción", "Observaciones"), show="headings")
    tree.heading("Cantidad", text="Cantidad")
    tree.heading("Unidad", text="Unidad")
    tree.heading("Descripción", text="Descripción")
    tree.heading("Observaciones", text="Observaciones")
    tree.place(relx=0.05, rely=0.60, relwidth=0.9, relheight=0.2)  # Tamaño relativo

    #Ventana para vizualizar las autorizaciones cargadas
    def autorizaciones(tree):
    
        ventana = tk.Toplevel()
        ventana.title("Autorizaciones Guardadas")
        ventana.geometry("1300x600")

        tree = ttk.Treeview(ventana, columns=("ID","Tipo", "Solicitante", "Monto", "Fecha Limite","Fecha solicitud"), show="headings")
        for col in ("ID","Tipo", "Solicitante", "Monto", "Fecha Limite","Fecha solicitud"):
            tree.heading(col, text=col)
        tree.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.8)
        cargar_autorizaciones(tree)

    
    tk.Button(ventana, text="Agregar Artículo", command=lambda: agregar_articulo(entry_cantidad, entry_unidad, entry_articulo, entry_observaciones, tree)).place(relx=0.05, rely=0.85)


    tk.Button(ventana, text="Registrar Autorización", command=lambda: agregar_autorizacion(entry_consecutivo,
        combo_tipo, combo_solicitante, entry_puesto, entry_area, entry_fecha_solicitud, 
        entry_fecha_requerida, entry_proyecto, entry_monto, combo_proveedor, combo_instruccion, entry_flimite, tree)).place(relx=0.25, rely=0.85)

    tk.Button(ventana, text="Generar Excel", command=lambda: generar_excel(entry_consecutivo,
        combo_tipo, combo_solicitante, entry_puesto, entry_area, entry_fecha_solicitud, 
        entry_fecha_requerida, entry_proyecto, entry_monto, combo_proveedor, combo_instruccion, articulos_lista, tree, entry_flimite)).place(relx=0.45, rely=0.85)
    
    tk.Button(ventana,text="Autorizaciones Guardadas", command=lambda: autorizaciones(tree)).place(relx=0.65, rely=0.85)
    
    ventana.mainloop()