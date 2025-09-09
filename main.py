import traceback
import sys
import actualizacion

# Antes de cargar interfaz
actualizacion.verificar_actualizacion()

def main():
    from login import ventana_login
    ventana_login()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        with open("error.log", "w", encoding="utf-8") as f:
            f.write("Error inesperado:\n")
            f.write(traceback.format_exc())
        print("Ocurrió un error. Revisa el archivo error.log")
        sys.exit(1)
