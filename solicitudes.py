import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from database import conectar_bd
from openpyxl import load_workbook
import mysql.connector
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os


# Plantilla de solicitud de pago
TEMPLATE_PATH = "C:\Sistema_SPagos\Plantillas\Solicitud_Pago.xlsx"

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



# Función para llenar el formato Excel
def generar_excel(id_autorizacion, fecha_solicitud, monto, proyecto_contrato, instruccion, 
                  nombre_proveedor, rfc, email, clave_bancaria, cuenta_bancaria, banco, articulos):
    try:
        workbook = load_workbook(TEMPLATE_PATH)
        sheet = workbook.active

        # Datos generales de la solicitud
        sheet["J6"] = id_autorizacion  
        sheet["C9"] = fecha_solicitud
        sheet["H9"] = monto
        sheet["H33"] = proyecto_contrato
        sheet["C12"] = nombre_proveedor
        sheet["G15"] = rfc
        sheet["G18"] = email
        sheet["C18"] = clave_bancaria
        sheet["C22"] = cuenta_bancaria
        sheet["G22"] = banco
        sheet["C15"] = instruccion
        sheet["C25"] = articulos  



        file_path = f"solicitudes_pago/solicitud_{id_autorizacion}.xlsx"
        workbook.save(file_path)
        os.startfile(file_path)  # Abrir automáticamente el archivo generado

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


#Funcion para manejar el filtrado
def filtrar_autorizaciones(tree, entry_filtro):
    filtro = entry_filtro.get()
    cargar_autorizaciones(tree, filtro)


#Carga informacion de las autorizaciones
def cargar_autorizaciones(tree, filtro=""):

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

        # Si hay un filtro, buscar por solicitante, proyecto o fecha
        if filtro:
            query = """SELECT * FROM AutorizacionesCompra 
                       WHERE id_autorizacion LIKE %s OR fecha_requerida LIKE %s OR monto LIKE %s OR proyecto_contrato LIKE %s"""
            cursor.execute(query, (f"%{filtro}%", f"%{filtro}%", f"%{filtro}%"))
        else:
        #Se ejecuta la consulta
            query = "SELECT id_autorizacion, fecha_requerida, monto, proyecto_contrato FROM autorizacionescompra"
            cursor.execute(query)
            autorizaciones = cursor.fetchall()

        #Muestra resultados
        for autorizacion in autorizaciones:
            tree.insert("", "end", values=autorizacion)

    except mysql.connector.Error as e:
        messagebox.showerror(f"❌Error", "Error al cargar articulos: ", {e})

    finally:
        #Cierra el cursor y la conexion si fueron creados correctamente
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()


# GUI
def gestionar_solicitudes():
    ventana = tk.Tk()
    ventana.title("Gestión de Solicitudes de Pago")
    ventana.geometry("1100x500")

    # Campo para filtrar
    tk.Label(ventana, text="Buscar:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    entry_filtro = tk.Entry(ventana)
    entry_filtro.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    # Botón para aplicar el filtro
    tk.Button(ventana, text="Filtrar", command=lambda: filtrar_autorizaciones(tree, entry_filtro)).grid(row=0, column=2, padx=10, pady=5)

    # Tabla de solicitudes
    tree = ttk.Treeview(ventana, columns=("ID", "Fecha", "Monto", "Proyecto"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Fecha", text="Fecha")
    tree.heading("Monto", text="Monto")
    tree.heading("Proyecto", text="Proyecto")
    tree.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Botones de exportación
    # Botón para generar el Excel
    tk.Button(ventana, text="Generar Excel", command=lambda: generar_excel_desde_seleccion(tree)).grid(row=2, column=1, padx=10, pady=10)

    # Botón para generar el PDF
    tk.Button(ventana, text="Generar PDF", command=lambda: generar_pdf_desde_seleccion(tree)).grid(row=2, column=0, padx=10, pady=10)


    # Ajustar tamaño de columnas dinámicamente
    ventana.grid_columnconfigure(1, weight=1)
    ventana.grid_rowconfigure(1, weight=1)

    # Cargar todas las solicitudes al iniciar la ventana
    cargar_autorizaciones(tree)

    ventana.mainloop()


# Ejecutar el programa
if __name__ == "__main__":
    gestionar_solicitudes()

