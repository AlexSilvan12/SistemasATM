import tkinter.ttk
from prueba_solicitud import CargaSolicitud
from openpyxl import load_workbook
import mysql.connector
import tkinter as tk 

TEMPLATE_PATH= "C:\Sistema_SPagos\Plantillas\Solicitud_Pago.xlsx"
def generar_excel():
    try: 
        autorizaciones=CargaSolicitud.cargar_autorizaciones()
        proveedores=CargaSolicitud.cargar_proveedores()
        articulos=CargaSolicitud.cargar_articulos()
        
        excel_book = load_workbook(TEMPLATE_PATH)
        sheet = excel_book.active
    
        #Encabezados de la tabla autorizaciones
        sheet ["A1"] = "id_autorizacion"
        sheet ["B1"] = "fecha_solicitud"
        sheet ["C1"] = "monto"
        sheet ["D1"] = "instruccion"
        sheet ["E1"] = "fecha_requerida"

        #Encabezados de la tabla proveedores
        sheet ["A8"] = "nombre"
        sheet ["B8"] = "RFC"
        sheet ["C8"] = "email"
        sheet ["D8"] = "Clave Bancaria"
        sheet ["E8"] = "Cuenta Bancaria"
        sheet ["F8"] = "Banco"

        #Encabezados de la tabla articulos
        sheet ["G1"] = "Cantidad"
        sheet ["H1"] = "Unidad"
        sheet ["I1"] = "Articulo"
        sheet ["J1"] = "Observaciones"

        #Ciclo para insertar las autorizaciones
        for index, row in enumerate(autorizaciones):
            sheet[f'A{index+2}'] = row [0]
            sheet[f'B{index+2}'] = row [1]
            sheet[f'C{index+2}'] = row [2]
            sheet[f'D{index+2}'] = row [3]
            sheet[f'E{index+2}'] = row [4]

        #Ciclo para insertar a los proveedores
        for index, row in enumerate(proveedores):
            sheet[f'A{index+9}'] = row [0]
            sheet[f'B{index+9}'] = row [1]
            sheet[f'C{index+9}'] = row [2]
            sheet[f'D{index+9}'] = row [3]
            sheet[f'E{index+9}'] = row [4]
            sheet[f'F{index+9}'] = row [5]

        #Ciclko para insertar los articulo 
        for index, row in enumerate(articulos):
            sheet[f'G{index+2}'] = row [0]
            sheet[f'H{index+2}'] = row [1]
            sheet[f'I{index+2}'] = row [2]
            sheet[f'J{index+2}'] = row [3]
            
            
        excel_book.save("Solicitudes\Prueba7.xlsx")

    except mysql.connector.Error as e:
            print(f"❌Error al cargar autorizaciones: {e}")
ventana=tkinter.Tk()
ventana.title("Prueba de generacion de excel")
ventana.geometry("300x300")

tk.Button(ventana, text="Generar Excel", command= generar_excel).grid(row=2, column=3, padx=10, pady=10)

ventana.mainloop()


#--------------------------------------------------------------------------------------------------------------------------

