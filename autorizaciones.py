import tkinter as tk
from tkinter import messagebox
from database import conectar_bd
import proveedores
from openpyxl import load_workbook


def agregar_autorizacion(tipo, solicitante, puesto, area, fecha_solicitud, fecha_requerida, proyecto_contrato, monto, id_proveedor, cantidad, unidad, articulo, observaciones, instrucciones):

    if not (tipo and solicitante and puesto and area and fecha_solicitud and fecha_requerida and proyecto_contrato and monto and id_proveedor and cantidad and unidad and articulo):
        messagebox.showwarning("Campos vacíos", "Por favor, llena todos los campos.")
        return

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        query = """
        INSERT INTO AutorizacionesCompra (tipo_solicitud, solicitante, puesto, area, fecha_solicitud, fecha_requerida, proyecto_contrato, monto, id_proveedor, cantidad, unidad, articulo, observaciones, instruccion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (tipo, solicitante, puesto, area, fecha_solicitud, fecha_requerida, proyecto_contrato, monto, id_proveedor, cantidad, unidad, articulo, observaciones, instrucciones)
        cursor.execute(query, valores)
        id_autorizacion = cursor.lastrowid
        conexion.commit()

        generar_excel(id_autorizacion, tipo, solicitante, puesto, area, fecha_solicitud, fecha_requerida, proyecto_contrato, monto, id_proveedor, cantidad, unidad, articulo, observaciones, instrucciones)

        messagebox.showinfo("Éxito", "Autorización registrada correctamente y guardada en Excel.")
        proveedores.cargar_proveedores()

        cursor.close()
        conexion.close()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo registrar la autorización: {e}")

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


