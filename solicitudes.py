import tkinter as tk
from tkinter import messagebox
from database import conectar_bd
from openpyxl import load_workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# Plantilla de solicitud de pago
TEMPLATE_PATH = "Solicitud_Pago.xlsx"

# Ventana para la gestión de solicitudes de pago
def cargar_autorizaciones():
    try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_autorizacion FROM AutorizacionesCompra")
            autorizaciones = cursor.fetchall()
            combo_autorizacion['values'] = [f"{a[0]} - {a[1]}" for a in autorizaciones]
            cursor.close()
            conexion.close()
    except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las autorizaciones: {e}")

def generar_documentos():
    id_autorizacion = combo_autorizacion.get().split(" - ")[0]

    if not id_autorizacion:
            messagebox.showwarning("Selección requerida", "Por favor, selecciona una autorización de compra.")
    return

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT a.id_autorizacion, a.fecha_solicitud, a.monto, a.proyecto_contrato, a.articulo, a.instruccion,
                   p.nombre, p.rfc, p.email, p.clave_bancaria, p.cuenta_bancaria, p.banco
            FROM AutorizacionesCompra a
            JOIN Proveedores p ON a.id_proveedor = p.id_proveedor
            WHERE a.id_autorizacion = %s
            """, (id_autorizacion,))
        datos = cursor.fetchone()

        if not datos:
                messagebox.showerror("Error", "No se encontraron datos para la autorización seleccionada.")
        return

        (id_autorizacion, fecha_solicitud, monto, proyecto_contrato, articulo, instruccion,
        nombre_proveedor, rfc, email, clave_bancaria, cuenta_bancaria, banco) = datos
            
        generar_excel(id_autorizacion, fecha_solicitud, monto, proyecto_contrato, articulo, instruccion,
                          nombre_proveedor, rfc, email, clave_bancaria, cuenta_bancaria, banco)
            
        messagebox.showinfo("Éxito", "Los documentos han sido generados correctamente.")
        cursor.close()
        conexion.close()

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar los documentos: {e}")

def generar_excel(id_autorizacion, fecha_solicitud, monto, proyecto_contrato, articulo, instruccion,
                       nombre_proveedor, rfc, email, clave_bancaria, cuenta_bancaria, banco):
        try:
            workbook = load_workbook(TEMPLATE_PATH)
            sheet = workbook.active

            sheet["J6"] = id_autorizacion  # Número de solicitud
            sheet["C9"] = fecha_solicitud
            sheet["H9"] = monto
            sheet["H33"] = proyecto_contrato
            sheet["C12"] = nombre_proveedor
            sheet["G15"] = rfc
            sheet["G18"] = email
            sheet["C18"] = clave_bancaria
            sheet["C22"] = cuenta_bancaria
            sheet["G22"] = banco
            sheet["C25"] = articulo  # Concepto de pago
            sheet["C15"] = instruccion  # Instrucción

            file_path = f"solicitudes_pago/solicitud_{id_autorizacion}.xlsx"
            workbook.save(file_path)
            os.startfile(file_path)  # Abrir automáticamente el archivo
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el archivo Excel: {e}")
