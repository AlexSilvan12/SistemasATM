import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from database import conectar_bd
from openpyxl import load_workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# Plantilla de solicitud de pago
TEMPLATE_PATH = "Solicitud_Pago.xlsx"

# Función para conectar con las solicitudes almacenadas en la base de datos
def cargar_solicitudes(tree):
    for row in tree.get_children():
        tree.delete(row)  # Limpiar datos previos

    conexion = None
    cursor = None

    try:
        conexion = conectar_bd()
        if conexion is None:
            print("❌ No se pudo establecer la conexión")
            return

        cursor = conexion.cursor()
        cursor.execute("SELECT id_solicitud, fecha_solicitud, importe, proyecto_contrato FROM SolicitudesPago")

        for solicitud in cursor.fetchall():
            tree.insert("", "end", values=solicitud)

        print("✅ Solicitudes de Pago cargadas correctamente.")

    except Exception as e:
        print(f"❌ Error al cargar solicitudes de pago: {e}")

    finally:
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()

# Función para llenar el formato Excel
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

def generar_pdf(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Atención", "Seleccione una solicitud para generar el PDF.")
        return

    solicitud = tree.item(selected_item, "values")
    id_solicitud = solicitud[0]
    ruta_pdf = convertir_solicitud_a_pdf(id_solicitud)

    if ruta_pdf:
        os.startfile(ruta_pdf)  # Abrir el PDF generado automáticamente


# Función para generar PDF
def convertir_solicitud_a_pdf(id_solicitud):
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

# GUI
def gestionar_solicitudes():
    ventana = tk.Tk()  # Se usa `Tk()` en lugar de `Toplevel()` para que sea la ventana principal
    ventana.title("Gestión de Solicitudes de Pago")
    ventana.geometry("700x500")

    tree = ttk.Treeview(ventana, columns=("ID", "Fecha", "Monto", "Proyecto"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Fecha", text="Fecha")
    tree.heading("Monto", text="Monto")
    tree.heading("Proyecto", text="Proyecto")
    tree.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
    tree.pack()

    tk.Button(ventana, text="Generar PDF", command=lambda: generar_pdf(tree)).pack()
    tk.Button(ventana, text="Generar Excel", command=lambda: generar_excel)

    cargar_solicitudes(tree)

    ventana.mainloop()  # Se necesita para mantener la ventana abierta

# Ejecutar el programa
if __name__ == "__main__":
    gestionar_solicitudes()

