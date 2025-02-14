import tkinter as tk
from tkinter import ttk, messagebox
from solicitudes import generar_excel
from database import conectar_bd

def ventana_gestion_solicitudes():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Solicitudes de Pago")
    ventana.geometry("600x400")

    tk.Label(ventana, text="Ingrese ID de Autorización:").grid(row=0, column=0, padx=10, pady=5)
    entry_id = tk.Entry(ventana)
    entry_id.grid(row=0, column=1, padx=10, pady=5)

    def generar_documentos():
        id_autorizacion = entry_id.get()
        if not id_autorizacion:
            messagebox.showwarning("Advertencia", "Debe ingresar un ID de autorización.")
            return
        
        ruta_excel = f"solicitudes_pago/solicitud_{id_autorizacion}.xlsx"
        ruta_pdf = f"solicitudes_pago/solicitud_{id_autorizacion}.pdf"

        generar_excel(id_autorizacion)
        

    btn_generar = tk.Button(ventana, text="Generar Solicitud", command=generar_documentos)
    btn_generar.grid(row=1, column=0, columnspan=2, pady=10)
