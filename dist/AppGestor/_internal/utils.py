import stat
import sys
from tkinter import messagebox
import os
import time
import win32com.client
import pythoncom

def ruta_relativa(ruta_relativa):
    """ Obtiene la ruta correcta del archivo, tanto en desarrollo como en el ejecutable """
    if getattr(sys, 'frozen', False):  # Si el programa está en un .exe
        base_path = sys._MEIPASS  # Carpeta temporal donde PyInstaller extrae los archivos
    else:
        base_path = os.path.abspath(".")  # Carpeta normal si ejecutas el script sin compilar

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


def convertir_excel_a_pdf(ruta_excel, ruta_pdf):
    pythoncom.CoInitialize()
    excel = None
    wb = None

    try:
        # Eliminar el archivo PDF si ya existe y está desbloqueado
        if os.path.exists(ruta_pdf):
            try:
                os.chmod(ruta_pdf, stat.S_IWRITE)  # Quitar solo lectura si tiene
                os.remove(ruta_pdf)
            except PermissionError:
                messagebox.showerror("❌ Error", f"No se puede sobrescribir {ruta_pdf} porque está en uso.")
                return False

        # Iniciar Excel (sin mostrarlo)
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False

        # Abrir workbook sin solo lectura
        wb = excel.Workbooks.Open(os.path.abspath(ruta_excel), ReadOnly=False)
        hoja = wb.Worksheets(1)

        # Configurar márgenes y escala para ajuste a página
        hoja.PageSetup.Zoom = False
        hoja.PageSetup.FitToPagesWide = 1
        hoja.PageSetup.FitToPagesTall = 1
        hoja.PageSetup.Orientation = 2  # Horizontal (Landscape)

        hoja.PageSetup.LeftMargin = hoja.PageSetup.Application.InchesToPoints(0.3)
        hoja.PageSetup.RightMargin = hoja.PageSetup.Application.InchesToPoints(0.3)
        hoja.PageSetup.TopMargin = hoja.PageSetup.Application.InchesToPoints(0.5)
        hoja.PageSetup.BottomMargin = hoja.PageSetup.Application.InchesToPoints(0.5)

        # Intentar exportar el archivo a PDF
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

        # Quitar solo lectura del PDF por seguridad
        if os.path.exists(ruta_pdf):
            os.chmod(ruta_pdf, stat.S_IWRITE)

        messagebox.showinfo("✅ Éxito", f"PDF generado: {ruta_pdf}")
        return True

    except Exception as e:
        messagebox.showerror("❌ Error", f"No se pudo convertir a PDF:\n{e}")
        return False

    finally:
        time.sleep(0.5)  # Esperar antes de cerrar Excel
        if wb:
            wb.Close(False)
        if excel:
            excel.Quit()
        import gc
        del wb, hoja, excel
        gc.collect()

        pythoncom.CoUninitialize()
        time.sleep(2)

def salir(callback, ventana):
    ventana.destroy()
    callback()