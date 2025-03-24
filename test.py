from database import conectar_bd
import mysql.connector
from autorizaciones import limpiar_formulario, limpiar_tabla

def generar_seleccion(tree):

    for row in tree.get_children():
        tree.delete(row)  

    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Atención", "Seleccione una autorización.")
        return

    id_autorizacion = tree.item(selected[0], "values")[0]
   
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

    generar_excel()

    

def generar_excel(entry_consecutivo, combo_tipo, entry_solicitante, entry_puesto, entry_area, 
                  entry_fecha_solicitud, entry_fecha_requerida, entry_proyecto, entry_monto, 
                  combo_proveedor, combo_instruccion, articulos, tree, entry_flimite):

    try:
        plantilla_path = "Plantillas\\Autorizaciones.xlsx"
        workbook = load_workbook(plantilla_path)
        sheet = workbook.active

        consecutivo = entry_consecutivo.get()
        tipo_solicitud = combo_tipo.get()
        solicitante = entry_solicitante.get()
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
        output_path = f"C:/Sistema_SPagos/Autorizaciones/Autorizacion_{consecutivo}.xlsx"
        workbook.save(output_path)
        os.startfile(output_path)

        # 🧹 Limpiar y recargar
        limpiar_formulario(entry_consecutivo, combo_tipo, entry_solicitante, entry_puesto, entry_area, 
                           entry_fecha_solicitud, entry_fecha_requerida, entry_proyecto, entry_monto, 
                           combo_proveedor, combo_instruccion, entry_flimite)
        cargar_autorizaciones(tree)
        articulos_lista.clear()
        limpiar_tabla(tree)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el archivo Excel: {e}")
