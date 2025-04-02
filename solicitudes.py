import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from database import conectar_bd
from openpyxl import load_workbook
import mysql.connector
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
        cursor.execute("""
    SELECT id_autorizacion, fecha_solicitud, monto, proyecto_contrato
    FROM autorizacionescompra
    WHERE id_autorizacion NOT IN (
        SELECT id_autorizacion FROM SolicitudesPago
    )
""")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar autorizaciones: {e}")
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()

# Función principal para generar el Excel desde la selección del Treeview
def generar_excel_desde_seleccion(tree, entry_consecutivo, entry_concepto, entry_referencia, entry_factura):
    id_solicitud = entry_consecutivo.get().strip()
    concepto = entry_concepto.get().strip()
    referencia_pago = entry_referencia.get().strip()
    factura = entry_factura.get().strip()
    
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

        cursor.execute("SELECT COUNT(*) FROM SolicitudesPago WHERE id_solicitud = %s", (id_solicitud,))
        if cursor.fetchone()[0] > 0:
            messagebox.showwarning("Advertencia", f"Ya existe una solicitud con el ID '{id_solicitud}'. No se generó el Excel ni se guardaron datos.")
            return

        # Autorización
        cursor.execute("""
            SELECT fecha_solicitud, monto, proyecto_contrato, instruccion, id_proveedor, fecha_limite_pago 
            FROM autorizacionescompra 
            WHERE id_autorizacion = %s
        """, (id_autorizacion,))
        autorizacion = cursor.fetchone()
        if not autorizacion:
            messagebox.showerror("Error", "No se encontró la autorización.")
            return

        fecha_solicitud, monto, proyecto_contrato, instruccion, id_proveedor, fechalimite = autorizacion

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
  

    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"No se pudo generar la solicitud: {e}")

        # Insertar en la tabla SolicitudesPago
    try:
            conexion = conectar_bd()
            cursor = conexion.cursor()

            # Verificar si ya existe el ID
            cursor.execute("SELECT COUNT(*) FROM SolicitudesPago WHERE id_solicitud = %s", (id_solicitud,))
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning("Advertencia", f"Ya existe una solicitud con el ID '{id_solicitud}'. No se guardó en la tabla.")
            else:
                query = """
                    INSERT INTO SolicitudesPago (
                    id_solicitud, id_autorizacion, id_proveedor, fecha_solicitud, 
                    importe, instruccion, referencia_pago, concepto, 
                    fecha_recibido_revision, fecha_limite_pago, num_facturas, proyecto_contrato
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
                cursor.execute(query, (
                id_solicitud, id_autorizacion, id_proveedor, fecha_solicitud,
                monto, instruccion, referencia_pago, concepto, fecha_solicitud, fechalimite, factura, proyecto_contrato
            ))
            conexion.commit()
            messagebox.showinfo("✅ Éxito", f"Solicitud '{id_solicitud}' guardada en la base de datos.")
            entry_consecutivo.delete(0, tk.END)
            entry_referencia.delete(0, tk.END)
            entry_concepto.delete(0, tk.END)
            entry_factura.delete(0,tk.END)

                # 🔄 Recargar el Treeview
            cargar_autorizaciones(tree)

    except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo registrar la solicitud en la base de datos:\n{err}")
    finally:
            if cursor: cursor.close()
            if conexion: conexion.close()

    # Generar el archivo Excel
    generar_excel(id_solicitud, fecha_solicitud, monto, proyecto_contrato, instruccion,
                  referencia_pago, fechalimite, concepto, factura, *proveedor)


# Función que llena la plantilla Excel con los datos
def generar_excel(id_solicitud, fecha_solicitud, monto, proyecto_contrato, instruccion,
                  referencia_pago, fechalimite, concepto, factura, nombre, rfc, email, clave_bancaria, cuenta_bancaria, banco):
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
        escribir(29, 8, fechalimite, combinar="H29:L29")         # H29 - Limite de Pago
        escribir(34, 3, factura, combinar="C34:F34")             # C34 - Numero de factura
        escribir(15, 3, instruccion, combinar="C15:E15")         # C15 - Instrucción
        escribir(22, 10, referencia_pago, combinar="J22:L22")    # J22 - Referencia de pago
        escribir(25, 3, concepto, combinar="C25:L25")            # C25 - Concepto

        # Guardar y abrir
        nombre_archivo = f"Solicitudes\\solicitud_{id_solicitud}.xlsx"
        wb.save(nombre_archivo)

        messagebox.showinfo("✅ Éxito", f"Archivo generado: {nombre_archivo}")
        os.startfile(nombre_archivo)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el Excel:\n{e}")


# Interfaz gráfica
def gestionar_solicitudes():
    ventana = tk.Toplevel()
    ventana.title("Solicitudes de Pago")
    ventana.geometry("1000x600")

    # Buscar
    tk.Label(ventana, text="Buscar:").place(relx=0.05, rely=0.02)
    entry_busqueda = tk.Entry(ventana, width=50)
    entry_busqueda.place(relx=0.1, rely=0.02)

    def buscar(*args):  # Acepta *args por el trace
        termino = entry_busqueda.get().lower()
        for item in tree.get_children():
            tree.delete(item)

        conexion = conectar_bd()
        cursor = conexion.cursor()
        if termino:
            consulta = """
                SELECT id_autorizacion, fecha_solicitud, monto, proyecto_contrato FROM autorizacionescompra
                WHERE LOWER(id_autorizacion) LIKE %s
                OR LOWER(fecha_solicitud) LIKE %s
                OR LOWER(monto) LIKE %s
                OR LOWER(proyecto_contrato) LIKE %s       
            """
            like_termino = f"%{termino}%"
            cursor.execute(consulta, (like_termino, like_termino, like_termino, like_termino))

        else : 
            consulta= ("""
                SELECT id_autorizacion, fecha_solicitud, monto, proyecto_contrato
                FROM autorizacionescompra
                WHERE id_autorizacion NOT IN (
                    SELECT id_autorizacion FROM SolicitudesPago
                )""")
            cursor.execute(consulta)
            
        resultados = cursor.fetchall()
        conexion.close()

        for row in resultados:
            tree.insert("", tk.END, values=row)

    entry_busqueda_var = tk.StringVar()
    entry_busqueda.config(textvariable=entry_busqueda_var)
    entry_busqueda_var.trace("w", buscar)  # Búsqueda automática al escribir

    # Consecutivo
    tk.Label(ventana, text="Consecutivo de Solicitud:").place(relx=0.05, rely=0.08)
    entry_consecutivo = tk.Entry(ventana, width=30)
    entry_consecutivo.place(relx=0.20, rely=0.08)

    # Concepto
    tk.Label(ventana, text="Concepto:").place(relx=0.05, rely=0.14)
    entry_concepto = tk.Entry(ventana, width=70)
    entry_concepto.place(relx=0.12, rely=0.14)

    # Referencia de Pago
    tk.Label(ventana, text="Referencia de Pago:").place(relx=0.05, rely=0.20)
    entry_referencia = tk.Entry(ventana, width=40)
    entry_referencia.place(relx=0.17, rely=0.20)

    #Numero de Factura
    tk.Label(ventana, text="Numero de Factura:").place(relx=0.05, rely=0.26)
    entry_factura = tk.Entry(ventana, width=30)
    entry_factura.place(relx=0.17, rely=0.26)

    # Treeview (tabla)
    tree = ttk.Treeview(ventana, columns=("ID", "Fecha", "Monto", "Proyecto"), show="headings")
    for col in ("ID", "Fecha", "Monto", "Proyecto"):
        tree.heading(col, text=col)

    # Scrollbar
    scrollbar = ttk.Scrollbar(ventana, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.place(relx=0.05, rely=0.32, relwidth=0.88, relheight=0.55)
    scrollbar.place(relx=0.93, rely=0.32, relheight=0.55)

    # Ventana de solicitudes guardadas
    def Solicitudes():
        ventana_solicitudes = tk.Toplevel(ventana)
        ventana_solicitudes.title("Solicitudes Guardadas")
        ventana_solicitudes.geometry("1100x600")

        tree_local = ttk.Treeview(ventana_solicitudes, columns=("ID", "fecha", "Importe", "Proyecto/Contrato", "Concepto"), show="headings")
        for col in ("ID", "fecha", "Importe", "Proyecto/Contrato", "Concepto"):
            tree_local.heading(col, text=col)

        tree_local.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar_local = ttk.Scrollbar(ventana_solicitudes, orient="vertical", command=tree_local.yview)
        tree_local.configure(yscrollcommand=scrollbar_local.set)
        scrollbar_local.pack(side="right", fill="y")

        cargar_solicitudes(tree_local)

    # Botones
    tk.Button(ventana, text="Generar Excel",
              command=lambda: generar_excel_desde_seleccion(tree, entry_consecutivo, entry_concepto, entry_referencia, entry_factura)
             ).place(relx=0.40, rely=0.88)

    tk.Button(ventana, text="Solicitudes Guardadas", command=Solicitudes).place(relx=0.58, rely=0.88)

    cargar_autorizaciones(tree)
    ventana.mainloop()