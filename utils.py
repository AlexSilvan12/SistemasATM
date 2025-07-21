import stat
import sys
from tkinter import messagebox
import os
import time
import stat
import platform
import subprocess

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



def salir(callback, ventana):
    ventana.destroy()
    callback()

def convertir_excel_a_pdf(ruta_excel, ruta_pdf):
    sistema = platform.system()

    if sistema == "Windows":
        try:
            import pythoncom
            import win32com.client
        except ImportError:
            messagebox.showerror("❌ Error", "No se encontraron las bibliotecas de automatización de Excel para Windows.")
            return False

        pythoncom.CoInitialize()
        excel = None
        wb = None

        try:
            if os.path.exists(ruta_pdf):
                try:
                    os.chmod(ruta_pdf, stat.S_IWRITE)
                    os.remove(ruta_pdf)
                except PermissionError:
                    messagebox.showerror("❌ Error", f"No se puede sobrescribir {ruta_pdf} porque está en uso.")
                    return False

            excel = win32com.client.DispatchEx("Excel.Application")
            excel.Visible = False
            wb = excel.Workbooks.Open(os.path.abspath(ruta_excel), ReadOnly=False)
            hoja = wb.Worksheets(1)

            hoja.PageSetup.Zoom = False
            hoja.PageSetup.FitToPagesWide = 1
            hoja.PageSetup.FitToPagesTall = 1
            hoja.PageSetup.Orientation = 2  # Horizontal

            hoja.PageSetup.LeftMargin = hoja.PageSetup.Application.InchesToPoints(0.3)
            hoja.PageSetup.RightMargin = hoja.PageSetup.Application.InchesToPoints(0.3)
            hoja.PageSetup.TopMargin = hoja.PageSetup.Application.InchesToPoints(0.5)
            hoja.PageSetup.BottomMargin = hoja.PageSetup.Application.InchesToPoints(0.5)

            for intento in range(5):
                try:
                    wb.ExportAsFixedFormat(0, os.path.abspath(ruta_pdf))
                    break
                except Exception as e:
                    if "0x800ac472" in str(e):
                        print("⏳ Excel ocupado, reintentando...")
                        time.sleep(1)
                    else:
                        raise
            else:
                raise Exception("Excel ocupado. No se pudo exportar a PDF.")

            if os.path.exists(ruta_pdf):
                os.chmod(ruta_pdf, stat.S_IWRITE)

            messagebox.showinfo("✅ Éxito", f"PDF generado: {ruta_pdf}")
            return True

        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo convertir a PDF:\n{e}")
            return False

        finally:
            time.sleep(0.5)
            if wb:
                wb.Close(False)
            if excel:
                excel.Quit()
            import gc
            del wb, hoja, excel
            gc.collect()
            pythoncom.CoUninitialize()
            time.sleep(1)

    elif sistema == "Darwin":  # macOS
        try:
            ruta_excel = os.path.abspath(ruta_excel)
            ruta_pdf = os.path.abspath(ruta_pdf)

            script = f'''
            tell application "Microsoft Excel"
                open POSIX file "{ruta_excel}"
                set activeWorkbook to active workbook
                tell activeWorkbook
                    save workbook as active sheet filename POSIX file "{ruta_pdf}" file format PDF file format
                    close saving no
                end tell
            end tell
            '''

            subprocess.run(["osascript", "-e", script], check=True)

            if os.path.exists(ruta_pdf):
                os.chmod(ruta_pdf, stat.S_IWRITE)

            messagebox.showinfo("✅ Éxito", f"PDF generado: {ruta_pdf}")
            return True

        except subprocess.CalledProcessError as e:
            messagebox.showerror("❌ Error", f"No se pudo generar el PDF con Excel en macOS:\n{e}")
            return False

    else:
        messagebox.showwarning("❌ No compatible", "La conversión a PDF solo está disponible en Windows y macOS.")
        return False
