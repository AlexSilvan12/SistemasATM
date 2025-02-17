import tkinter as tk
from UI.main_menu import abrir_menu

def iniciar_interfaz():
    root = tk.Tk()
    root.title("Sistema de Solicitudes de Pago")
    root.geometry("400x300")
    abrir_menu(root)
    root.mainloop()
