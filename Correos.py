import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import os
from database import conectar_bd 


def enviar_documentos_a_contador(usuario_actual):
    # Seleccionar archivos .pdf y .xlsx
    archivos = filedialog.askopenfilenames(
        title="Selecciona los documentos a enviar",
        filetypes=[("Archivos PDF y Excel", "*.pdf *.xlsx")]
    )

    if not archivos:
        messagebox.showinfo("Sin selección", "No seleccionaste ningún documento.")
        return

    # Obtener lista de contadores registrados
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre, email FROM usuarios WHERE rol = 'Contador'")
    contadores = cursor.fetchall()
    conexion.close()

    if not contadores:
        messagebox.showwarning("Sin contadores", "No hay contadores registrados en el sistema.")
        return

    # Crear ventana para seleccionar un contador
    seleccion_ventana = tk.Toplevel()
    seleccion_ventana.title("Seleccionar Contador")
    seleccion_ventana.geometry("400x300")

    tk.Label(seleccion_ventana, text="Seleccione el contador a quien enviar:", font=("Arial", 12, "bold")).pack(pady=10)

    listbox = tk.Listbox(seleccion_ventana, font=("Arial", 11))
    for nombre, email in contadores:
        listbox.insert(tk.END, f"{nombre} ({email})")
    listbox.pack(fill="both", expand=True, padx=20, pady=10)

    def enviar_seleccion():
        seleccion = listbox.curselection()
        if not seleccion:
            messagebox.showwarning("Selecciona un contador", "Por favor selecciona un contador.")
            return
        
        contador_seleccionado = contadores[seleccion[0]]  # (nombre, email)
        contador_email = contador_seleccionado[1]

        # Solicitar contraseña del usuario actual
        contraseña = simpledialog.askstring("Contraseña requerida", f"Ingrese la contraseña del correo {usuario_actual['email']}:", show="*")
        if not contraseña:
            messagebox.showwarning("Contraseña requerida", "No se ingresó ninguna contraseña.")
            return
        
        # Enviar correo
        if enviar_documento_por_correo(
            remitente_email=usuario_actual["email"],
            remitente_password=contraseña,
            archivos_paths=archivos,
            asunto="Documentos Autorizados",
            cuerpo="Estimado contador, se envían los documentos autorizados para su proceso correspondiente.",
            destinatario_email=contador_email
        ):
            messagebox.showinfo("✅ Enviado", "Documentos enviados con éxito.")
            seleccion_ventana.destroy()
        else:
            messagebox.showerror("❌ Error", "No se pudo enviar el correo.")

    tk.Button(seleccion_ventana, text="Enviar Documentos", command=enviar_seleccion, bg="green", fg="white", font=("Arial", 11, "bold")).pack(pady=10)
    tk.Button(seleccion_ventana, text="Cancelar", command=seleccion_ventana.destroy, bg="red", fg="white", font=("Arial", 11, "bold")).pack()

    seleccion_ventana.mainloop()


def enviar_documentos_a_gerente(usuario_actual):
    # Seleccionar archivos .pdf y .xlsx
    archivos = filedialog.askopenfilenames(
        title="Selecciona los documentos a enviar",
        filetypes=[("Archivos PDF y Excel", "*.pdf *.xlsx")]
    )

    if not archivos:
        messagebox.showinfo("Sin selección", "No seleccionaste ningún documento.")
        return

    # Buscar el email de la gerente
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT email FROM usuarios WHERE rol = 'Gerente'")
    resultado = cursor.fetchone()
    conexion.close()

    if not resultado:
        messagebox.showerror("Error", "No se encontró una gerente registrada.")
        return

    gerente_email = resultado[0]

    # Solicitar contraseña del usuario actual
    contraseña = simpledialog.askstring("Contraseña requerida", f"Ingrese la contraseña del correo {usuario_actual['email']}:", show="*")
    if not contraseña:
        messagebox.showwarning("Contraseña requerida", "No se ingresó ninguna contraseña.")
        return

    # Enviar correo
    if enviar_documento_por_correo(
        remitente_email=usuario_actual["email"],
        remitente_password=contraseña,
        archivos_paths=archivos,
        asunto="Nuevos Documentos de Autorización",
        cuerpo="Gerente, se envían los documentos para su autorización.",
        destinatario_email=gerente_email
    ):
        messagebox.showinfo("✅ Enviado", "Documentos enviados a la Gerente con éxito.")
    else:
        messagebox.showerror("❌ Error", "No se pudo enviar el correo.")


def enviar_documento_por_correo(remitente_email, remitente_password, archivos_paths, asunto, cuerpo, destinatario_email):
    try:
        # Crear mensaje
        mensaje = MIMEMultipart()
        mensaje['From'] = remitente_email
        mensaje['To'] = destinatario_email
        mensaje['Subject'] = asunto

        # Cuerpo del mensaje
        mensaje.attach(MIMEText(cuerpo, 'plain'))

        # Adjuntar archivos
        for archivo_path in archivos_paths:
            with open(archivo_path, 'rb') as archivo:
                extension = os.path.splitext(archivo_path)[1].lower()
                tipo = "pdf" if extension == ".pdf" else "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                adjunto = MIMEApplication(archivo.read(), _subtype=tipo)
                adjunto.add_header('Content-Disposition', 'attachment', filename=os.path.basename(archivo_path))
                mensaje.attach(adjunto)

        # Conectar al servidor SMTP
        servidor = smtplib.SMTP('smtp.office365.com', 587)  
        servidor.starttls()
        servidor.login(remitente_email, remitente_password)
        servidor.send_message(mensaje)
        servidor.quit()

        print("✅ Correo enviado con éxito.")
        return True

    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")
        return False
