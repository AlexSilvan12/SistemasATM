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

        if id_autorizacion:
            generar_excel(id_autorizacion, tipo, solicitante, puesto, area, fecha_solicitud, fecha_requerida, proyecto_contrato, monto, id_proveedor, instruccion)
        else:
            messagebox.showerror("❌Error", "No se pudo generar el archivo Excel.")

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


def gestionar_autorizaciones():

    ventana = tk.Tk()
    ventana.title("Gestión de Autorizaciones de Compra")
    ventana.geometry("900x900")

    tk.Label(ventana, text="Tipo de Solicitud: ").grid(row=1, column=0, padx=10, pady=5)
    combo_tipo = ttk.Combobox(ventana, values=["Maquinaria", "Equipo y/o Htas", "Servicios", "EPP"])
    combo_tipo.grid(row=1, column=1, padx= 10, pady= 5)

    tk.Label(ventana, text="Solicitante:").grid(row=2, column=0, padx=10, pady=5)
    entry_solicitante= tk.Entry(ventana)
    entry_solicitante.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Puesto:").grid(row=3, column=0, padx=10, pady=5)
    entry_puesto = tk.Entry(ventana)
    entry_puesto.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Area:").grid(row=4, column=0, padx=10, pady=5)
    entry_area = tk.Entry(ventana)
    entry_area.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Fecha de Solicitud:").grid(row=5, column=0, padx=10, pady=5)
    entry_fecha_solicitud = tk.Entry(ventana)
    entry_fecha_solicitud.grid(row=5, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Fecha Requerida:").grid(row=6, column=0, padx=10, pady=5)
    entry_fecha_requerida = tk.Entry(ventana)
    entry_fecha_requerida.grid(row=6, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Proyecto y/o contrato:").grid(row=7, column=0, padx=10, pady=5)
    entry_proyecto = tk.Entry(ventana)
    entry_proyecto.grid(row=7, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Monto (solo valor numérico):").grid(row=8, column=0, padx=10, pady=5)
    entry_monto = tk.Entry(ventana)    
    entry_monto.grid(row=8, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Proveedor:").grid(row=9, column=0, padx=10, pady=5)  
    proveedores = cargar_proveedores()
    combo_proveedor = ttk.Combobox(ventana, values=proveedores)  # Se pasa la lista como argumento
    combo_proveedor.grid(row=9, column=1, padx=20, pady=10)

    tk.Label(ventana, text="Cantidad:").grid(row=10, column=0, padx=10, pady=5)
    entry_cantidad = tk.Entry(ventana)
    entry_cantidad.grid(row=10, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Unidad:").grid(row=11, column=0, padx=10, pady=5)
    entry_unidad = ttk.Combobox(ventana, values=["Piezas", "Litros", "Kilos", "Metros", "Otros"])
    entry_unidad.grid(row=11, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Descripcion:").grid(row=12, column=0, padx=10, pady=5) 
    entry_articulo = tk.Entry(ventana)
    entry_articulo.grid(row=12, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Observaciones:").grid(row=13, column=0, padx=25, pady=25)
    entry_observaciones = tk.Entry(ventana)
    entry_observaciones.grid(row=13, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Instruccion: ").grid(row=14, column=0, padx=10, pady=5)
    combo_instruccion = ttk.Combobox(ventana, values=["Transferencia Electronica", "Tarjeta de Debito", "Efectivo"])
    combo_instruccion.grid(row=14, column=1, padx=10, pady=5)

    #Tabla de articulos
    tk.Label(ventana, text="Artículos:").grid(row=15, column=0, padx=10, pady=5)
    tree = ttk.Treeview(ventana, columns=("Cantidad", "Unidad", "Descripcion", "Observaciones"), show="headings")
    tree.heading("Cantidad", text="Cantidad")
    tree.heading("Unidad", text="Unidad")
    tree.heading("Descripcion", text="Descripcion")
    tree.heading("Observaciones", text="Observaciones")
    tree.grid(row=15, column=0, columnspan=2, padx=10, pady=5)

    tk.Button(ventana, text="Registrar Autorización", command=lambda: agregar_autorizacion(
    combo_tipo, entry_solicitante, entry_puesto, entry_area, entry_fecha_solicitud, 
    entry_fecha_requerida, entry_proyecto, entry_monto, combo_proveedor, combo_instruccion)).grid(row=16, column=0, columnspan=2, pady=10)

    tk.Button(ventana, text="Agregar Artículo", command=lambda: agregar_articulo(entry_cantidad, entry_unidad, entry_articulo, entry_observaciones, tree)).grid(row=16, column=1, columnspan=2, pady=10)
    cargar_autorizaciones(tree)

    ventana.mainloop()

if __name__ == "__main__":
    gestionar_autorizaciones()