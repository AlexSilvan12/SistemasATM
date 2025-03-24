import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from database import conectar_bd
from openpyxl import load_workbook
import mysql.connector
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from openpyxl.styles import Alignment

# Plantilla de solicitud de pago
TEMPLATE_PATH = "Plantillas\Solicitud_Pago.xlsx"

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
        cursor.execute("SELECT id_solicitud, fecha_solicitud, importe, proyecto_contrato, concepto FROM SolicitudesPago")

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


def cargar_autorizaciones(tree):
    tree.delete(*tree.get_children())  # Limpiar tabla

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_autorizacion, fecha_solicitud, monto, proyecto_contrato FROM autorizacionescompra")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar autorizaciones: {e}")
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()

# Función principal para generar el Excel desde la selección del Treeview
def generar_excel_desde_seleccion(tree, entry_consecutivo):

    id_solicitud = entry_consecutivo.get().strip()

    if not id_solicitud:
        messagebox.showwarning("Consecutivo vacío", "Debes ingresar un consecutivo para la solicitud.")
        return

    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Atención", "Seleccione una autorización.")
        return

    id_autorizacion = tree.item(selected[0], "values")[0]

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        # Autorización
        cursor.execute("""
            SELECT fecha_solicitud, monto, proyecto_contrato, instruccion, id_proveedor 
            FROM autorizacionescompra 
            WHERE id_autorizacion = %s
        """, (id_autorizacion,))
        autorizacion = cursor.fetchone()
        if not autorizacion:
            messagebox.showerror("Error", "No se encontró la autorización.")
            return

        fecha_solicitud, monto, proyecto_contrato, instruccion, id_proveedor = autorizacion

        # Proveedor
        cursor.execute("""
            SELECT nombre, rfc, email, clave_bancaria, cuenta_bancaria, banco
            FROM proveedores
            WHERE id_proveedor = %s
        """, (id_proveedor,))
        proveedor = cursor.fetchone()
        if not proveedor:
            messagebox.showerror("Error", "No se encontró el proveedor.")
            return

        # Artículos
        cursor.execute("""
            SELECT cantidad, unidad, articulo, observaciones
            FROM articulosautorizacion
            WHERE id_autorizacion = %s
        """, (id_autorizacion,))
        articulos = cursor.fetchall()

        cursor.close()
        conexion.close()   

    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"No se pudo generar la solicitud: {e}")

        # Insertar en la tabla SolicitudesPago
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Verificar si ya existe el ID
            cursor.execute("SELECT COUNT(*) FROM SolicitudesPago WHERE id_solicitud = %s", (id_autorizacion,))
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning("Advertencia", f"Ya existe una solicitud con el ID '{id_autorizacion}'. No se guardó en la tabla.")
            else:
                query = """
                    INSERT INTO SolicitudesPago (id_solicitud, fecha_solicitud, importe, proyecto_contrato)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (id_autorizacion, fecha_solicitud, monto, proyecto_contrato))
                conexion.commit()
                messagebox.showinfo("✅ Éxito", f"Solicitud '{id_autorizacion}' guardada en la base de datos.")
                
                entry_consecutivo.delete(0, tk.END)


                # 🔄 Recargar el Treeview
                cargar_solicitudes(tree)

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo registrar la solicitud en la base de datos:\n{err}")
        finally:
            if cursor: cursor.close()
            if conexion: conexion.close()

    # Generar el archivo Excel
    generar_excel(id_solicitud, fecha_solicitud, monto, proyecto_contrato, instruccion, *proveedor, articulos)


# Función que llena la plantilla Excel con los datos
def generar_excel(id_solicitud, fecha_solicitud, monto, proyecto_contrato, instruccion,
                  nombre, rfc, email, clave_bancaria, cuenta_bancaria, banco, articulos):
    try:
        wb = load_workbook(TEMPLATE_PATH)
        sheet = wb.active

        # Función para escribir en celdas combinadas
        def escribir(fila, columna, valor, combinar=None):
            celda = sheet.cell(row=fila, column=columna)

            # Verificar si está en un rango combinado
            for r in sheet.merged_cells.ranges:
                if celda.coordinate in r:
                    sheet.unmerge_cells(str(r))
                    break

            celda.value = valor
            celda.alignment = Alignment(horizontal="center", vertical="center")

            # Si se desea recombinar
            if combinar:
                sheet.merge_cells(combinar)

        # Llenar celdas con datos generales
        escribir(6, 10, id_solicitud, combinar="J6:L6")          # J6 - Consecutivo
        escribir(9, 3, fecha_solicitud, combinar="C9:E9")        # C9 - Fecha
        escribir(9, 8, monto, combinar="H9:L9")                  # H9 - Monto
        escribir(34, 8, proyecto_contrato, combinar="H34:L34")   # H33 - Proyecto

        escribir(12, 3, nombre, combinar="C12:L12")              # C12 - Nombre proveedor
        escribir(15, 7, rfc, combinar="G15:L15")                 # G15 - RFC
        escribir(18, 8, email, combinar="H18:L18")               # G18 - Email
        escribir(18, 3, clave_bancaria, combinar="C18:F18")      # C18 - Clave bancaria
        escribir(22, 3, cuenta_bancaria, combinar="C22:E22")     # C22 - Cuenta bancaria
        escribir(22, 7, banco, combinar="G22:H22")               # G22 - Banco
        escribir(15, 3, instruccion, combinar="C15:E15")         # C15 - Instrucción

        # Llenar artículos (comienza en fila 25)
        fila_inicio = 25
        for i, (cantidad, unidad, articulo, observaciones) in enumerate(articulos):
            fila = fila_inicio + i
            escribir(fila, 4, cantidad)        # Columna D
            escribir(fila, 5, unidad)          # Columna E
            escribir(fila, 6, articulo)        # Columna F
            escribir(fila, 8, observaciones)   # Columna H

        # Guardar y abrir
        nombre_archivo = f"C:/Sistema_SPagos/Solicitudes/solicitud_{id_solicitud}.xlsx"
        wb.save(nombre_archivo)

        messagebox.showinfo("✅ Éxito", f"Archivo generado: {nombre_archivo}")
        os.startfile(nombre_archivo)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el Excel:\n{e}")


# Interfaz gráfica
def gestionar_solicitudes():
    ventana = tk.Tk()
    ventana.title("Solicitudes de Pago")
    ventana.geometry("950x500")

    frame_filtro = tk.Frame(ventana)
    frame_filtro.pack(pady=10)

    tk.Label(frame_filtro, text="Buscar:").pack(side="left", padx=5)
    entry_filtro = tk.Entry(frame_filtro)
    entry_filtro.pack(side="left", padx=5)

    # NUEVO: Campo para ingresar el consecutivo
    frame_consecutivo = tk.Frame(ventana)
    frame_consecutivo.pack(pady=5)

    tk.Label(frame_consecutivo, text="Consecutivo de Solicitud:").pack(side="left", padx=5)
    entry_consecutivo = tk.Entry(frame_consecutivo)
    entry_consecutivo.pack(side="left", padx=5)


    tree = ttk.Treeview(ventana, columns=("ID", "Fecha", "Monto", "Proyecto"), show="headings")
    for col in ("ID", "Fecha", "Monto", "Proyecto"):
        tree.heading(col, text=col)
    tree.place(relx=0.05, rely=0.15, relwidth=0.9, relheight=0.7)

    def Solicitudes(tree):
    
        ventana = tk.Tk()
        ventana.title("Autorizaciones Guardadas")
        ventana.geometry("1300x600")

        tree = ttk.Treeview(ventana, columns=("ID", "fecha", "Importe", "Proyecto/Contrato", "Concepto"), show="headings")
        for col in ("ID", "fecha", "Importe", "Proyecto/Contrato"):
            tree.heading(col, text=col)
        tree.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.8)
        cargar_solicitudes(tree)

    tk.Button(ventana, text="Generar Excel", command=lambda: generar_excel_desde_seleccion(tree, entry_consecutivo)).place(relx=0.45, rely=0.9)

    tk.Button(ventana,text="Solicitudes Guardadas", command=lambda: Solicitudes(tree)).place(relx=0.65, rely=0.9)

    cargar_autorizaciones(tree)
    ventana.mainloop()

# Ejecutar la app
if __name__ == "__main__":
    gestionar_solicitudes()