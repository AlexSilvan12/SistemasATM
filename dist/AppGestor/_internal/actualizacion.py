import requests
import os
import subprocess
import sys
from tkinter import messagebox
from utils import ruta_relativa

VERSION_LOCAL_PATH = ruta_relativa("version_local.txt")
URL_VERSION = "https://raw.githubusercontent.com/AlexSilvan12/SistemasATM/refs/heads/main/version.txt"

def obtener_version_local():
    try:
        with open(VERSION_LOCAL_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "0.0.0"

def verificar_actualizacion():
    try:
        response = requests.get(URL_VERSION, timeout=5)
        lineas = response.text.strip().splitlines()
        version_remota = lineas[0].strip()
        url_instalador = lineas[1].strip()

        version_local = obtener_version_local()
        if version_remota > version_local:
            respuesta = messagebox.askyesno("🆕 Actualización disponible",
                                            f"Versión {version_remota} disponible. ¿Deseas actualizar?")
            if respuesta:
                ejecutar_instalador(version_remota, url_instalador)
    except Exception as e:
        print(f"❌ Error al verificar actualización: {e}")

def ejecutar_instalador(version, url):
    try:
        from tempfile import gettempdir
        nombre_instalador = os.path.join(gettempdir(), f"Instalador_AppGestor_{version}.exe")

        r = requests.get(url, stream=True)
        with open(nombre_instalador, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        with open(VERSION_LOCAL_PATH, "w", encoding="utf-8") as f:
            f.write(version)

        subprocess.Popen(nombre_instalador, shell=True)
        sys.exit()

    except Exception as e:
        messagebox.showerror("❌ Error", f"No se pudo aplicar la actualización:\n{e}")
