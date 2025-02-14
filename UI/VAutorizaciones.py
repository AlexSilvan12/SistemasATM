import tkinter as tk
from tkinter import ttk, messagebox
#import database
import proveedores

def ventana_gestion_autorizaciones():
   

    ventana = tk.Toplevel()
    ventana.title("Gestión de Autorizaciones de Compra")
    ventana.geometry("900x600")

    tk.Label(ventana, text="Tipo de Solicitud: ").grid(row=1, column=0, padx=10, pady=5)
    combo_tipo = tk.Combobox(ventana, values=["Maquinaria", "Equipo y/o Htas", "Servicios", "EPP"])
    combo_tipo.grid(row=1, column=1, padx= 10, pady= 5)

    tk.Label(ventana, text="Solicitante:").grid(row=2, column=0, padx=10, pady=5)
    entry_solicitante= tk.Entry(ventana)
    entry_solicitante.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Puesto:").grid(row=3, column=0, padx=10, pady=5)
    entry_puesto = tk.Entry(ventana)
    entry_puesto.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Area:").grid(row=4, column=0, padx=10, pady=5)
    entry_area = tk.Entry(ventana)
    entry_area.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Fecha de Solicitud:").grid(row=5, column=0, padx=10, pady=5)
    entry_fecha_solicitud = tk.Entry(ventana)
    entry_fecha_solicitud.grid(row=5, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Fecha Requerida:").grid(row=6, column=0, padx=10, pady=5)
    entry_fecha_requerida = tk.Entry(ventana)
    entry_fecha_requerida.grid(row=6, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Proyecto y/o contrato:").grid(row=7, column=0, padx=10, pady=5)
    entry_proyecto = tk.Entry(ventana)
    entry_proyecto.grid(row=7, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Monto:").grid(row=8, column=0, padx=10, pady=5)
    entry_monto = tk.Entry(ventana)    
    entry_monto.grid(row=8, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Cantidad:").grid(row=9, column=0, padx=10, pady=5)
    entry_cantidad = tk.Entry(ventana)
    entry_cantidad.grid(row=9, column=1, padx=10, pady=5)
    tk.Label(ventana, text="Unidad:").grid(row=10, column=0, padx=10, pady=5)
    entry_unidad = ttk.Combobox(ventana)
    entry_unidad.grid(row=10, column=1, padx=10, pady=5)
    tk.Label(ventana, text="Artículo:").grid(row=11, column=0, padx=10, pady=5)
    entry_articulo = tk.Entry(ventana)
    entry_articulo.grid(row=11, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Observaciones:").grid(row=12, column=0, padx=10, pady=5)
    entry_observaciones = tk.Entry(ventana)
    entry_observaciones.grid(row=12, column=1, padx=10, pady=5)
    tk.Label(ventana, text="Proveedor:").grid(row=13, column=0, padx=10, pady=5)  
    combo_proveedor = ttk.Combobox(ventana, values=[proveedores.cargar_proveedores()])
    combo_proveedor.grid(row=13, column=1, padx=10, pady=5)

    tk.Label(ventana, text="Instruccion: ").grid(row=14, column=0, padx=10, pady=5)
    combo_instruccion = ttk.Combobox(ventana, values=["Transferencia Electronica", "Tarjeta de Debito", "Efectivo"])
    combo_instruccion.grid(row=14, column=1, padx=10, pady=5)

    tk.Button(ventana, text="Registrar Autorización", command=proveedores.agregar_autorizacion).grid(row=15, column=0, columnspan=2, pady=10)
    proveedores.cargar_proveedores()
