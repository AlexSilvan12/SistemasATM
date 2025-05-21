import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk 
from database import conectar_bd
import mysql.connector
import os
import time
import win32com.client
import pythoncom

import sys
import os

def ruta_relativa(ruta_relativa):
    """Obtiene la ruta correcta del archivo, tanto en desarrollo como en el ejecutable"""
    if getattr(sys, 'frozen', False):
        # Cuando se ejecuta como ejecutable (.exe)
        base_path = sys._MEIPASS
    else:
        # Cuando se ejecuta como script (.py)
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, ruta_relativa)

def centrar_ventana(ventana, ancho, alto):
    # Obtén las dimensiones de la pantalla
    screen_width = ventana.winfo_screenwidth()
    screen_height = ventana.winfo_screenheight()

    # Calcula la posición x, y para centrar la ventana
    pos_x = (screen_width // 2) - (ancho // 2)
    pos_y = (screen_height // 2) - (alto // 2)

    # Establece la geometría de la ventana con la posición calculada
    ventana.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")

import time

def convertir_excel_a_pdf(ruta_excel, ruta_pdf):
    pythoncom.CoInitialize()
    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False

    try:
        wb = excel.Workbooks.Open(os.path.abspath(ruta_excel))
        hoja = wb.Worksheets(1)

        hoja.PageSetup.Zoom = False
        hoja.PageSetup.FitToPagesWide = 1
        hoja.PageSetup.FitToPagesTall = 1
        hoja.PageSetup.Orientation = 2  # xlLandscape

        hoja.PageSetup.LeftMargin = hoja.PageSetup.Application.InchesToPoints(0.3)
        hoja.PageSetup.RightMargin = hoja.PageSetup.Application.InchesToPoints(0.3)
        hoja.PageSetup.TopMargin = hoja.PageSetup.Application.InchesToPoints(0.5)
        hoja.PageSetup.BottomMargin = hoja.PageSetup.Application.InchesToPoints(0.5)

        time.sleep(1)

        # 🔁 Reintentar si Excel está ocupado
        for intento in range(5):
            try:
                wb.ExportAsFixedFormat(0, os.path.abspath(ruta_pdf))  # 0 = PDF
                break
            except Exception as e:
                if "0x800ac472" in str(e):
                    print("⏳ Excel ocupado, reintentando...")
                    time.sleep(1)
                else:
                    raise
        else:
            raise Exception("Excel ocupado. No se pudo exportar a PDF.")

        messagebox.showinfo("✅ Éxito", f"PDF generado: {ruta_pdf}")
        return True

    except Exception as e:
        messagebox.showerror("❌ Error", f"No se pudo convertir a PDF:\n{e}")
        return False

    finally:
        time.sleep(0.5)
        wb.Close(False)
        excel.Quit()
        pythoncom.CoUninitialize()

        # ✅ Abrir el PDF solo si fue creado correctamente
        if os.path.exists(ruta_pdf):
            try:
                time.sleep(0.5)  # Esperar medio segundo adicional por seguridad
                os.startfile(ruta_pdf)
            except Exception as e:
                print(f"⚠️ No se pudo abrir el PDF automáticamente: {e}")

