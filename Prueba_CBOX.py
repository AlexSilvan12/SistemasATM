from tkinter import Tk, Label, Button, ttk
import tkinter as tk
from proveedores import cargar_proveedores  # Importa tu función real

# Ventana
ventana = Tk()
ventana.title("Proveedores")
ventana.geometry("500x200")

# Variable para lista completa
proveedores_originales = []

# Combobox
combo_proveedor = ttk.Combobox(ventana)
combo_proveedor.place(relx=0.2, rely=0.65, relwidth=0.4)

# Etiqueta
Label(ventana, text="Proveedor:", font=("Arial", 10, "bold"), bg="#ffebeb").place(relx=0.05, rely=0.65)

# Función para actualizar combobox con la lista original
def actualizar_combobox_proveedores():
    global proveedores_originales
    proveedores = cargar_proveedores()
    if proveedores:
        proveedores_originales = proveedores
        combo_proveedor['values'] = proveedores_originales

# Función de filtrado al escribir
def filtrar_proveedores(event):
    texto = combo_proveedor.get().lower()
    if not texto:
        combo_proveedor['values'] = proveedores_originales
    else:
        filtrados = [p for p in proveedores_originales if texto in p.lower()]
        combo_proveedor['values'] = filtrados

# Asociar evento de escritura
combo_proveedor.bind("<KeyRelease>", filtrar_proveedores)

# Botón para actualizar desde la base de datos
Button(ventana, text="Actualizar", command=actualizar_combobox_proveedores).place(relx=0.63, rely=0.65)

# Cargar al inicio
actualizar_combobox_proveedores()

ventana.mainloop()