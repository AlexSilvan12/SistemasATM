import tkinter as tk
from tkinter import ttk
from openpyxl import load_workbook
from openpyxl.styles import Font
import os

# Ruta del archivo de Excel
file_path = "C:/Sistema_SPagos/Plantillas/Autorizaciones.xlsx"

# Función para actualizar el Excel con la selección
def actualizar_excel():
    tipo_solicitud = tipo_combobox.get()  # Obtener el valor seleccionado en Combobox
    
    # Cargar el archivo
    workbook = load_workbook(file_path)
    sheet = workbook.active

    # Mapeo de tipos de solicitud a celdas en Excel
    tipo_a_celda = {
        "Maquinaria": "C10",
        "Equipo y/o Htas": "E10",
        "Servicios": "G10",
        "Otros": "H9"
    }

    # Limpiar cualquier "X" anterior en las celdas C10, D10, G10, H10
    for celda in tipo_a_celda.values():
        sheet[celda].value = ""

    # Insertar la "X" en la celda correcta si el tipo de solicitud es válido
    if tipo_solicitud in tipo_a_celda:
        celda_obj = sheet[tipo_a_celda[tipo_solicitud]]
        celda_obj.value = "X"
        celda_obj.font = Font(bold=True, color="FF0000")  # Negrita y rojo

    # Guardar los cambios
    workbook.save("C:/Sistema_SPagos/Autorizaciones/Autorizaciones_Modificado3.xlsx")
    print("✅ Archivo actualizado correctamente")

    os.startfile("C:/Sistema_SPagos/Autorizaciones/Autorizaciones_Modificado3.xlsx")

# Crear ventana Tkinter
ventana = tk.Tk()
ventana.title("Seleccionar Tipo de Solicitud")

# Label
tk.Label(ventana, text="Selecciona el tipo de solicitud:").pack()

# Crear Combobox
opciones = ["Maquinaria", "Equipo y/o Htas", "Servicios", "Otros"]
tipo_combobox = ttk.Combobox(ventana, values=opciones, state="readonly")
tipo_combobox.pack()
tipo_combobox.set(opciones[0])  # Valor por defecto

# Botón para actualizar el Excel
tk.Button(ventana, text="Actualizar Excel", command=actualizar_excel).pack()

ventana.mainloop()
