from tkinter import messagebox
from database import conectar_bd
import autorizaciones
from openpyxl import load_workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# Plantilla de solicitud de pago
TEMPLATE_PATH = "Solicitud_Pago.xlsx"

# Ventana para la gestión de solicitudes de pago
def cargar_solicitudes():
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_solicitud, fecha_solicitud, monto, proyecto_contrato FROM SolicitudesPago")
        solicitudes = cursor.fetchall()
        cursor.close()
        conexion.close()
        return solicitudes
    except Exception as e:
        print(f"Error al cargar solicitudes de pago: {e}")
        return []


def generar_documentos():
    id_autorizacion = autorizaciones.combo_autorizacion.get().split(" - ")[0]

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

def generar_pdf(id_solicitud):
    try:
        ruta_excel = f"solicitudes_pago/solicitud_{id_solicitud}.xlsx"
        ruta_pdf = f"solicitudes_pago/solicitud_{id_solicitud}.pdf"
        
        workbook = load_workbook(ruta_excel)
        sheet = workbook.active
        
        c = canvas.Canvas(ruta_pdf, pagesize=letter)
        c.drawString(100, 750, f"Solicitud de Pago - ID: {id_solicitud}")
        c.drawString(100, 730, f"Fecha: {sheet['B3'].value}")
        c.drawString(100, 710, f"Monto: {sheet['B4'].value}")
        c.drawString(100, 690, f"Proyecto: {sheet['B5'].value}")
        c.drawString(100, 670, f"Proveedor: {sheet['B6'].value}")
        c.save()
        
        return ruta_pdf
    except Exception as e:
        print(f"Error al convertir solicitud a PDF: {e}")
        return None