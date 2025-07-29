import sys
import zipfile
import requests
import shutil
from tkinter import messagebox
import os
from utils import ruta_relativa

VERSION_LOCAL = ruta_relativa("version_local.txt")
URL_VERSION = "https://raw.githubusercontent.com/AlexSilvan12/SistemasATM/desarrollo/Actualizacion/version.txt"
URL_ZIP = "https://github.com/AlexSilvan12/SistemasATM/releases/download/v1.0.2/Actualizacion_v1.0.2.zip"
def obtener_version_local():
    try:
        with open(VERSION_LOCAL, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "0.0.0"  # Si no existe el archivo, forzamos actualización

def verificar_actualizacion():
    try:
        version_local = obtener_version_local()
        response = requests.get(URL_VERSION, timeout=5)
        version_remota = response.text.strip()

        if version_remota > version_local:
            respuesta = messagebox.askyesno("🆕 Actualización disponible",
                                            f"Versión {version_remota} disponible. ¿Deseas actualizar?")
            if respuesta:
                descargar_y_aplicar(version_remota)
    except Exception as e:
        print(f"No se pudo verificar actualización: {e}")

def descargar_y_aplicar(nueva_version):
    try:
        ruta_zip = "actualizacion.zip"
        r = requests.get(URL_ZIP, stream=True)
        with open(ruta_zip, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        with zipfile.ZipFile(ruta_zip, 'r') as zip_ref:
            zip_ref.extractall("update_temp")

        os.remove(ruta_zip)

        for root, _, files in os.walk("update_temp"):
            for file in files:
                origen = os.path.join(root, file)
                destino = os.path.join(os.getcwd(), os.path.relpath(origen, "update_temp"))
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                shutil.move(origen, destino)

        shutil.rmtree("update_temp")

        # ✅ Actualiza el archivo de versión local
        with open(VERSION_LOCAL, "w", encoding="utf-8") as f:
            f.write(nueva_version)

        messagebox.showinfo("✅ Actualización", "La aplicación se actualizó. Se reiniciará ahora.")
        reiniciar_aplicacion()

    except Exception as e:
        messagebox.showerror("❌ Error", f"No se pudo actualizar:\n{e}")

def reiniciar_aplicacion():
    python = sys.executable
    os.execl(python, python, *sys.argv)
