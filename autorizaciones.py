import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from proveedores import cargar_proveedores
from database import conectar_bd
from openpyxl import load_workbook


def gestionar_autorizaciones():

    ventana = tk.Toplevel()
    ventana.title("Gestión de Autorizaciones de Compra")
    ventana.geometry("900x600")

    tk.Label(ventana, text="Tipo de Solicitud: ").grid(row=1, column=0, padx=10, pady=5)
    combo_tipo = tk.Combobox(ventana, values=["Maquinaria", "Equipo y/o Htas", "Servicios", "EPP"])
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

    tk.Label(ventana, text="Monto:").grid(row=8, column=0, padx=10, pady=5)
    entry_monto = tk.Entry(ventana)    
    entry_monto.grid(row=8, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Cantidad:").grid(row=9, column=0, padx=10, pady=5)
    entry_cantidad = tk.Entry(ventana)
    entry_cantidad.grid(row=9, column=1, padx=10, pady=5)
    tk.Label(ventana, text="Unidad:").grid(row=10, column=0, padx=10, pady=5)
    entry_unidad = ttk.Combobox(ventana)
    entry_unidad.grid(row=10, column=1, padx=10, pady=5)
    tk.Label(ventana, text="Artículo:").grid(row=11, column=0, padx=10, pady=5)
    entry_articulo = tk.Entry(ventana)
    entry_articulo.grid(row=11, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Observaciones:").grid(row=12, column=0, padx=10, pady=5)
    entry_observaciones = tk.Entry(ventana)
    entry_observaciones.grid(row=12, column=1, padx=10, pady=5)
    tk.Label(ventana, text="Proveedor:").grid(row=13, column=0, padx=10, pady=5)  
    combo_proveedor = ttk.Combobox(ventana, values=[cargar_proveedores()])
    combo_proveedor.grid(row=13, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Instruccion: ").grid(row=14, column=0, padx=10, pady=5)
    combo_instruccion = ttk.Combobox(ventana, values=["Transferencia Electronica", "Tarjeta de Debito", "Efectivo"])
    combo_instruccion.grid(row=14, column=1, padx=10, pady=5)

    tk.Button(ventana, text="Registrar Autorización", command=agregar_autorizacion).grid(row=15, column=0, columnspan=2, pady=10)
    cargar_autorizaciones()


def agregar_autorizacion(combo_tipo, entry_solicitante, entry_puesto, entry_area, entry_fecha_solicitud, entry_fecha_requerida, entry_proyecto, entry_monto, combo_proveedor,entry_cantidad, entry_unidad, entry_articulo, entry_observaciones, combo_instruccion):
    tipo = combo_tipo.get()
    solicitante = entry_solicitante.get()
    puesto = entry_puesto.get()
    area = entry_area.get()
    fecha_solicitud = entry_fecha_solicitud.get()
    fecha_requerida = entry_fecha_requerida.get()
    proyecto_contrato = entry_proyecto.get()
    monto = entry_monto.get()
    id_proveedor = combo_proveedor.get().split(" - ")[0]
    cantidad = entry_cantidad.get()
    unidad = entry_unidad.get()
    articulo = entry_articulo.get()
    observaciones = entry_observaciones.get()
    instruccion = combo_instruccion.get()


    if not (tipo and solicitante and puesto and area and fecha_solicitud and fecha_requerida and proyecto_contrato and monto and id_proveedor and cantidad and unidad and articulo and observaciones and instruccion):
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

        #Ejecuta la consulta
        query = """
        INSERT INTO AutorizacionesCompra (tipo_solicitud, solicitante, puesto, area, fecha_solicitud, fecha_requerida, proyecto_contrato, monto, id_proveedor, cantidad, unidad, articulo, observaciones, instruccion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (tipo, solicitante, puesto, area, fecha_solicitud, fecha_requerida, proyecto_contrato, monto, id_proveedor, cantidad, unidad, articulo, observaciones, instruccion)
        cursor.execute(query, valores)
        id_autorizacion = cursor.lastrowid
        conexion.commit()

        #Muestra resultado
        print("✅Éxito: Autorización registrada correctamente y guardada en Excel.")
        messagebox.showinfo("✅Éxito", "Autorización registrada correctamente y guardada en Excel.")

        #Limpia el formulario despues de ingresar los datos
        limpiar_formulario()
        cargar_autorizaciones()

        if id_autorizacion:
            generar_excel(id_autorizacion, tipo, solicitante, puesto, area, fecha_solicitud, fecha_requerida, proyecto_contrato, monto, id_proveedor, cantidad, unidad, articulo, observaciones, instruccion)
        else:
            messagebox.showerror("❌Error", "No se pudo generar el archivo Excel.")

    except mysql.connector.Error as e:
        print(f"❌Error al agregar autorizacion: {e}")    

    finally:
        #Cierra el cursor y la conexion si fueron creados correctamente
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()
        

def cargar_autorizaciones():
        
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
        proveedores = cursor.fetchall()

        #Muestra resultados
        print("✅Lista de autorizaciones: ")
        for row in proveedores:
            print (row) 

    except mysql.connector.Error as e:
        print(f"❌Error al cargar autorizaciones: {e}")

    finally:
        #Cierra el cursor y la conexion si fueron creados correctamente
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()


def limpiar_formulario(combo_tipo, entry_solicitante, entry_puesto, entry_area, entry_fecha_solicitud, entry_fecha_requerida, entry_proyecto, entry_monto, combo_proveedor,entry_cantidad, entry_unidad, entry_articulo, entry_observaciones, combo_instruccion):
    combo_tipo.delete(0, tk.END)
    entry_solicitante.delete(0, tk.END)
    entry_puesto.get(0, tk.END)
    entry_area.get(0, tk.END)
    entry_fecha_solicitud.get(0, tk.END)
    entry_fecha_requerida.get(0, tk.END)
    entry_proyecto.get(0, tk.END)
    entry_monto.get(0, tk.END)
    entry_cantidad.get(0, tk.END)
    entry_unidad.get(0, tk.END)
    entry_articulo.get(0, tk.END)
    entry_observaciones.get(0, tk.END) 

def generar_excel(id_autorizacion, tipo, solicitante, puesto, area, fecha_solicitud, fecha_requerida, proyecto_contrato, monto, id_proveedor, cantidad, unidad, articulo, observaciones, instrucciones):
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
        sheet["17"] = cantidad
        sheet["C17"] = unidad
        sheet["D17"] = articulo
        sheet["G17"] = observaciones
        sheet["B30"] = instrucciones

        workbook.save(f"autorizaciones/autorizacion_{id_autorizacion}.xlsx")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el archivo Excel: {e}")
