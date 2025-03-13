import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from proveedores import cargar_proveedores
from database import conectar_bd
from openpyxl import load_workbook

#Funcion para agregar las autorizaciones
def agregar_autorizacion(entry_consecutivo, combo_tipo, entry_solicitante, entry_puesto, entry_area, entry_fecha_solicitud, entry_fecha_requerida, entry_proyecto, entry_monto, combo_proveedor, combo_instruccion):
    consecutivo = entry_consecutivo.get()
    tipo = combo_tipo.get()
    solicitante = entry_solicitante.get()
    puesto = entry_puesto.get()
    area = entry_area.get()
    fecha_solicitud = entry_fecha_solicitud.get()
    fecha_requerida = entry_fecha_requerida.get()
    proyecto_contrato = entry_proyecto.get()
    monto = entry_monto.get()
    id_proveedor = combo_proveedor.get().split(" - ")[0]
    instruccion = combo_instruccion.get()


    if not (tipo and solicitante and puesto and area and fecha_solicitud and fecha_requerida and proyecto_contrato and monto and id_proveedor and instruccion):
        messagebox.showwarning("Campos vacíos", "Por favor, llena todos los campos.")
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

        #Ejecuta la consulta para insertar la autorizacion
        query = """
        INSERT INTO AutorizacionesCompra (id_autorizacion, tipo_solicitud, solicitante, puesto, area, fecha_solicitud, fecha_requerida, proyecto_contrato, monto, id_proveedor, instruccion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        

        valores = (consecutivo, tipo, solicitante, puesto, area, fecha_solicitud, fecha_requerida, proyecto_contrato, monto, id_proveedor, instruccion)
        cursor.execute(query, valores)
        id_autorizacion = cursor.lastrowid

        #ejecuta la consulta para insertar los articulos relacionados
        query_articulo = """
            INSERT INTO ArticulosAutorizacion (id_autorizacion, cantidad, unidad, articulo, observaciones)
            VALUES (%s, %s, %s, %s, %s)
        """

        if not articulos_lista:
            messagebox.showwarning("Advertencia", "Debe agregar al menos un artículo antes de registrar la autorización.")
            return
        
        for articulo in articulos_lista:
            cursor.execute(query_articulo, (id_autorizacion, *articulo))

        conexion.commit()

        #Muestra resultado
        messagebox.showinfo("✅Éxito", "Autorización y articulos registrados correctamente.")

        #Limpia el formulario despues de ingresar los datos
        limpiar_formulario()
        cargar_autorizaciones()


    except mysql.connector.Error as e:
        conexion.rollback()
        messagebox.showerror("❌Error", f"Error al agregar autorizacion: {e}")    

    finally:
        #Cierra el cursor y la conexion si fueron creados correctamente
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()
        articulos_lista.clear()

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
    entry_unidad.set("")
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
        query = "SELECT * FROM autorizacionescompra"
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
                       entry_fecha_requerida, entry_proyecto, entry_monto, combo_proveedor,
                        combo_instruccion):
    
    entry_consecutivo.delete(0, tk.END)
    combo_tipo.set("")  
    entry_solicitante.delete(0, tk.END)
    entry_puesto.delete(0, tk.END)
    entry_area.delete(0, tk.END)
    entry_fecha_solicitud.delete(0, tk.END)
    entry_fecha_requerida.delete(0, tk.END)
    entry_proyecto.delete(0, tk.END)
    entry_monto.delete(0, tk.END)
    combo_proveedor.set("")
    combo_instruccion.set("")


def generar_excel(id_autorizacion, tipo, solicitante, puesto, area, fecha_solicitud, fecha_requerida, proyecto_contrato, monto, id_proveedor, cantidad, unidad, articulo, observaciones, instrucciones, articulos):
    try:
        workbook = load_workbook("Autorizaciones.xlsx")
        sheet = workbook.active

        sheet["H6"] = id_autorizacion
        sheet["B3"] = tipo
        sheet["C12"] = solicitante
        sheet["A39"] = solicitante
        sheet["C13"] = puesto
        sheet["A40"] = puesto
        sheet["C14"] = area
        sheet["G12"] = fecha_solicitud
        sheet["G13"] = fecha_requerida
        sheet["G14"] = proyecto_contrato
        sheet["B32"] = monto
        sheet["B31"] = id_proveedor
        sheet["B30"] = instrucciones

        #Llenado de la tabla de los articulos
        fila_inicio = 17  # Supongamos que la tabla de artículos comienza en la fila 17
        for i, (cantidad, unidad, articulo, observaciones) in enumerate(articulos):
            sheet[f"B{fila_inicio + i}"] = cantidad
            sheet[f"C{fila_inicio + i}"] = unidad
            sheet[f"D{fila_inicio + i}"] = articulo
            sheet[f"G{fila_inicio + i}"] = observaciones

        workbook.save(f"autorizaciones/autorizacion_{id_autorizacion}.xlsx")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el archivo Excel: {e}")


def generar_excel_desde_seleccion(tree):
    selected_item = tree.selection()
    
    if not selected_item:
        messagebox.showwarning("Atención", "Seleccione una autorización para generar el Excel.")
        return

    solicitud = tree.item(selected_item, "values")
    if not solicitud:
        messagebox.showerror("Error", "No se pudo obtener la información de la solicitud.")
        return

    id_autorizacion = str(solicitud[0])  # Forzar que sea STRING
    print(f"📌 ID Autorización antes de consulta: {id_autorizacion} ({type(id_autorizacion)})")

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT fecha_solicitud, monto + 0, proyecto_contrato, instruccion, id_proveedor 
            FROM AutorizacionesCompra 
            WHERE CAST(id_autorizacion AS CHAR) = %s
        """, (id_autorizacion,))
        
        autorizacion = cursor.fetchone()
        if not autorizacion:
            messagebox.showerror("Error", "No se encontró la autorización de compra.")
            return

        fecha_solicitud, monto, proyecto_contrato, instruccion, id_proveedor = autorizacion

        try:
            monto = float(monto)  # Convertir a número decimal
        except ValueError:
            messagebox.showerror("Error", "El monto no es un número válido.")
            return

        cursor.execute("""
            SELECT nombre, rfc, email, clave_bancaria, cuenta_bancaria, banco 
            FROM Proveedores 
            WHERE id_proveedor = %s
        """, (id_proveedor,))
        
        proveedor = cursor.fetchone()
        if not proveedor:
            messagebox.showerror("Error", "No se encontró información del proveedor.")
            return

        cursor.execute("""
            SELECT cantidad, unidad, articulo, observaciones
            FROM ArticulosAutorizacion 
            WHERE id_autorizacion = %s
        """, (id_autorizacion,))
        
        articulos = cursor.fetchall()

        cursor.close()
        conexion.close()

        generar_excel(id_autorizacion, fecha_solicitud, monto, proyecto_contrato, 
                      instruccion, *proveedor, articulos)

    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"No se pudo obtener los datos: {e}")


def gestionar_autorizaciones():

    ventana = tk.Tk()
    ventana.title("Gestión de Autorizaciones de Compra")
    ventana.geometry("900x900")

    # Función para calcular posiciones relativas
    def pos(x, y):
        return {"relx": x, "rely": y, "anchor": "w"}  # Posiciona desde la izquierda
    
    tk.Label(ventana, text="Consecutivo: ").place(**pos(0.05, 0.05))
    entry_consecutivo = tk.Entry(ventana)
    entry_consecutivo.place(**pos(0.3, 0.05))


    tk.Label(ventana, text="Tipo de Solicitud: ").place(**pos(0.05, 0.10))
    combo_tipo = ttk.Combobox(ventana, values=["Maquinaria", "Equipo y/o Htas", "Servicios", "EPP"])
    combo_tipo.place(**pos(0.3, 0.10))

    tk.Label(ventana, text="Solicitante:").place(**pos(0.05, 0.15))
    entry_solicitante = tk.Entry(ventana)
    entry_solicitante.place(**pos(0.3, 0.15))

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

    tk.Label(ventana, text="Monto (solo valor numérico):").place(**pos(0.05, 0.45))
    entry_monto = tk.Entry(ventana)
    entry_monto.place(**pos(0.3, 0.45))

    tk.Label(ventana, text="Proveedor:").place(**pos(0.05, 0.50))
    proveedores = cargar_proveedores()
    combo_proveedor = ttk.Combobox(ventana, values=proveedores)
    combo_proveedor.place(**pos(0.3, 0.50))

    tk.Label(ventana, text="Cantidad:").place(**pos(0.55, 0.05))
    entry_cantidad = tk.Entry(ventana)
    entry_cantidad.place(**pos(0.75, 0.05))

    tk.Label(ventana, text="Unidad:").place(**pos(0.55, 0.10))
    entry_unidad = ttk.Combobox(ventana, values=["Piezas", "Litros", "Kilos", "Metros", "Otros"])
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

    # Tabla de artículos
    tk.Label(ventana, text="Artículos:").place(**pos(0.05, 0.55))
    tree = ttk.Treeview(ventana, columns=("Cantidad", "Unidad", "Descripción", "Observaciones"), show="headings")
    tree.heading("Cantidad", text="Cantidad")
    tree.heading("Unidad", text="Unidad")
    tree.heading("Descripción", text="Descripción")
    tree.heading("Observaciones", text="Observaciones")
    tree.place(relx=0.05, rely=0.60, relwidth=0.9, relheight=0.2)  # Tamaño relativo

    tk.Button(ventana, text="Registrar Autorización", command=lambda: agregar_autorizacion(entry_consecutivo,
        combo_tipo, entry_solicitante, entry_puesto, entry_area, entry_fecha_solicitud, 
        entry_fecha_requerida, entry_proyecto, entry_monto, combo_proveedor, combo_instruccion)).place(relx=0.05, rely=0.85)

    tk.Button(ventana, text="Agregar Artículo", command=lambda: agregar_articulo(entry_cantidad, entry_unidad, entry_articulo, entry_observaciones, tree)).place(relx=0.25, rely=0.85)

    tk.Button(ventana, text="Generar Excel", command=lambda: generar_excel_desde_seleccion(tree)).grid(row=2, column=1, padx=10, pady=10)
    
    cargar_articulos(tree)

    ventana.mainloop()

if __name__ == "__main__":
    gestionar_autorizaciones()