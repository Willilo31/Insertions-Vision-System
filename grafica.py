import customtkinter
import Jetson.GPIO as GPIO
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
import pandas as pd
from app8 import main
import threading
import os
import warnings
import variable

PINGREEN = 11
PINRED = 12
PINALARM = 13


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(PINGREEN, GPIO.OUT)
GPIO.setup(PINRED, GPIO.OUT)
GPIO.setup(PINALARM, GPIO.OUT)

GPIO.output(PINGREEN, True)
GPIO.output(PINRED, True)
GPIO.output(PINALARM, True)
GPIO.cleanup()

global iniciado
global order_value_label
global pause
global id_seleccionado

id_seleccionado = ''
pause = 0
iniciado = 0

customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

app = customtkinter.CTk() 
app.geometry("1000x700")
#app.geometry("640x480")
#app.attributes('-fullscreen', 'True')
app.title("Bad Insertions Verification")

# image = Image.open('Logo Baxter-01.png')
# image_tk = ImageTk.PhotoImage(image)
# label = tk.Label(app, image=image_tk)
# label.pack()

custom_font = customtkinter.CTkFont(family='Verdana', size=28)

# Crear campos de texto para mostrar los datos
Order_text = tk.StringVar()
line_text = tk.StringVar()
pn_text = tk.StringVar()
date_text = tk.StringVar()
turno_text = tk.StringVar()
status_text = tk.StringVar()


# # A que se debe este error que me esta saliendo y como puedo solucionarlo 
# def show_notification(message, duration=3000):  # 3000 milisegundos = 3 segundos
    
#     # Crear una nueva ventana emergente
#     popup = tk.Toplevel(app)  # Asume que 'app' es tu ventana principal
#     popup.overrideredirect(True)  # Oculta la barra de título de la ventana emergente

#     # Configurar el tamaño de fuente y otros estilos si es necesario
#     msg_font = ("Arial", 24)
#     popup.configure(bg="white")

#     # Añadir un mensaje a la ventana emergente
#     msg_label = tk.Label(popup, text=message, font=msg_font, bg="white")
#     msg_label.pack(pady=20, padx=20)

#     # Actualiza el tamaño de 'popup' para que se ajuste al contenido
#     popup.update_idletasks()

#     # Posición inicial (parte superior fuera de la vista)
#     x = app.winfo_x() + (app.winfo_width() // 2) - (popup.winfo_width() // 2)
#     y = app.winfo_y() - popup.winfo_height()
#     popup.geometry("+%d+%d" % (x, y))

#     # Define la animación de aparición
#     target_y = app.winfo_y()  # Posición final en y
#     delta_y = (target_y - y + 100) // 10  # Desplazamiento por fotograma

#     def animate_appear():
#         nonlocal y
#         if y < target_y:
#             y += delta_y
#             popup.geometry("+%d+%d" % (x, y))
#             popup.after(10, animate_appear)
#         else:
#             # Establecer un temporizador para iniciar la animación de desaparición después de 'duration' milisegundos
#             popup.after(duration, animate_disappear)

#     # Define la animación de desaparición
#     def animate_disappear():
#         nonlocal y
#         if y > (app.winfo_y() - popup.winfo_height()):
#             y -= delta_y
#             popup.geometry("+%d+%d" % (x, y))
#             popup.after(10, animate_disappear)
#         else:
#             popup.destroy()

#     # Aquí, en lugar de usar `popup.after(10, animate_appear)`, utilizamos `popup.after_idle(animate_appear)`
#     # Esto asegura que la animación comience solo después de que todos los otros eventos pendientes (como dibujar la ventana) estén completos.
#     popup.after(1, animate_appear)


def start_program():
    global selected_Order 
    global iniciado
    global order_value_label
    global pause

    if not selected_Order.get():
        # show_notification("Seleccione el número de orden")
        return

    if iniciado == 0:
        if not os.path.exists('historial de inserciones'):
            os.mkdir('historial de inserciones')

        # Crear el archivo CSV con el nombre del número de orden
        file_path = os.path.join('historial de inserciones', f"{selected_Order.get()}.csv")

        # Si el archivo no existe, crea uno con los encabezados
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                file.write('Item,Model,Defect Type,Time,Date\n')
        thread = threading.Thread(target=main, args=(selected_Order.get(), insert_table,), daemon=True)
        thread.start()
        iniciado = 1
        pause = 0
        order_value_label.config(state=tk.DISABLED)
        variable.STOPSYSTEM[0] = 0
    else:
        pass
        # show_notification("El programa ya ha iniciado")

def stop_program():
    global iniciado
    global pause

    if pause == 1:
        # show_notification("La orden ya esta pausada")
        pass

    if iniciado == 1:
        pause = 1
        variable.STOPSYSTEM[0] = 1
    elif iniciado == 0 and pause == 0:
        pass
        # show_notification("No se puede pausar la orden sin haber iniciado")  
    iniciado = 0

def complete_program():
    global pause
    global iniciado
    global order_value_label
    global view_camera_state

    if iniciado == 1 or pause == 1:
        stop_program()
        order_value_label.config(state=tk.NORMAL)
        # show_notification("El sistema ha finalizado con exito")
        selected_Order.set('')
        iniciado = 0
        pause = 0
    
    else:
        pass
        # show_notification("No se puede completar la orden sin haber iniciado")
camera_state = "Camera One"

# Esta función cambiará el texto del botón entre "Camera One", "Camera Two" y "Both Cameras" en el orden especificado.
def toggle_camera_text():
    global camera_state
    if camera_state == "Camera One":
        CameraBtn.configure(text="Camera Two")
        camera_state = "Camera Two"
    elif camera_state == "Camera Two":
        CameraBtn.configure(text="Both Cameras")
        camera_state = "Both Cameras"
    else:
        CameraBtn.configure(text="Camera One")
        camera_state = "Camera One"

view_camera_state = "View Camera OFF"

def view_camera():
    global view_camera_state
    global iniciado

    if iniciado == 1:
        if view_camera_state == "View Camera OFF":
            ViewCameraBtn.configure(text="View Camera ON")
            view_camera_state = "View Camera ON"
            variable.VIEWCAMARA[0] = 1
        else:
            ViewCameraBtn.configure(text="View Camera OFF")
            view_camera_state = "View Camera OFF"
            variable.VIEWCAMARA[0] = 0

    else:
        pass
        # show_notification("Primero inicia el sistema")

table = None
table_frame = ttk.Frame(app)

def insert_table():
    global id_seleccionado
    global table
    if table:
        for row in table.get_children():
            table.delete(row)

    if not table:
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side='right', fill='y')

        table = ttk.Treeview(table_frame, columns=("Item", "Model", "Defect Type", "Time", "Date"))
        vsb.config(command=table.yview)
        table['show'] = 'headings'

    # Agregar encabezados de columna
    table.heading("Item", text="Item")
    table.heading("Model", text="Model")
    table.heading("Defect Type", text="Defect Type")
    table.heading("Time", text="Time")
    table.heading("Date", text="Date")

    # Establecer el ancho de las columnas
    table.column("Item", width=50)
    table.column("Model", width=150)
    table.column("Defect Type", width=150)
    table.column("Time", width=100)
    table.column("Date", width=100)

    def add_row(Item, Model, DType, TimeVal, DateVal):
        table.insert("", "end", values=(Item, Model, DType, TimeVal, DateVal))

    file_path = f"historial de inserciones/{id_seleccionado}.csv"

    
    try:
        df1 = pd.read_csv(file_path)
        #print(df1)  # <-- Imprimir el contenido del DataFrame

        if not df1.empty:
            for _, row in df1.iterrows():
                #print(f"Agregando fila: {row.tolist()}")  # Debugging
                add_row(row['Item'], row['Model'], row['Defect Type'], row['Time'], row['Date'])
        else:
            print("El archivo está vacío o no contiene datos.")
    except FileNotFoundError:
        pass  

    table.pack(side='left', fill='both', expand=True)

def shutdown_system():
    global iniciado
    global pause
    if iniciado == 0 and pause == 0:
        # Muestra el cuadro de diálogo de confirmación
        response = messagebox.askyesno("Confirmación", "¿Seguro que quiere apagar el sistema?")
        
        # Si el usuario hace clic en 'Sí', cierra el programa
        if response:
            app.destroy()
        # Si el usuario hace clic en 'No', no hagas nada y regresa
        else:
            return
    else:
        pass
        # show_notification("Primero complete la orden")

def header():
    global order_value_label
    global selected_Order
    global id_seleccionado
    header_frame = tk.Frame(app, bg="black")

    order_label = tk.Label(header_frame, text="Order #:", fg="white", bg="black", font=("Arial", 14))
    pn_label = tk.Label(header_frame, text="PN:", fg="white", bg="black", font=("Arial", 14))
    pn_value_label = tk.Label(header_frame, textvariable=pn_text, fg="white", bg="black", font=("Arial", 14))

    line_label = tk.Label(header_frame, text="Line:", fg="white", bg="black", font=("Arial", 14))
    line_value_label = tk.Label(header_frame, textvariable=line_text, fg="white", bg="black", font=("Arial", 14))
    date_label = tk.Label(header_frame, text="Date:", fg="white", bg="black", font=("Arial", 14))
    date_value_label = tk.Label(header_frame, textvariable=date_text, fg="white", bg="black", font=("Arial", 14))
    
    Turno_label = tk.Label(header_frame, text="Turno:", fg="white", bg="black", font=("Arial", 14))
    Turno_value_label = tk.Label(header_frame, textvariable=turno_text, fg="white", bg="black", font=("Arial", 14))
    Status_label = tk.Label(header_frame, text="Status:", fg="white", bg="black", font=("Arial", 14))
    Status_value_label = tk.Label(header_frame, textvariable=status_text, fg="white", bg="black", font=("Arial", 14))

    order_label.grid(row=0, column=0, padx=10, pady=10)
    pn_label.grid(row=0, column=2, padx=10, pady=10)
    pn_value_label.grid(row=0, column=3, padx=10, pady=10)
    
    Turno_label.grid(row=0, column=4, padx=10, pady=10)
    Turno_value_label.grid(row=0, column=5, padx=10, pady=10)

    line_label.grid(row=1, column=0, padx=10, pady=10)
    line_value_label.grid(row=1, column=1, padx=10, pady=10)

    date_label.grid(row=1, column=2, padx=10, pady=10)
    date_value_label.grid(row=1, column=3, padx=10, pady=10)

    Status_label.grid(row=1, column=4, padx=10, pady=10)
    Status_value_label.grid(row=1, column=5, padx=10, pady=10)

    df = pd.read_csv('abc.csv')  # Reemplaza 'ruta_del_archivo.csv' con la ubicación real de tu archivo

    # Crear una variable de control para el valor seleccionado en la barra desplegable
    selected_Order = tk.StringVar()

    # Crear la barra desplegable
    order_value_label = tk.OptionMenu(header_frame, selected_Order, *df[(df['Status'] == 'In Use') | (df['Status'] == 'In Process')]['Order'])
    order_value_label.config(fg="white", bg="black", font=("Arial", 14))
    order_value_label['menu'].config(fg="white", bg="black", font=("Arial", 14))
    order_value_label.grid(row=0, column=1, padx=10, pady=10)  # Utiliza grid en lugar de pack dentro del header_frame

    def mostrar_datos(*args):
        # Obtener el ID seleccionado en la barra desplegable 
        global id_seleccionado
        id_seleccionado = selected_Order.get()
        insert_table()
        if id_seleccionado:
            # Filtrar los datos según el ID seleccionado y el estado "In Use" o "In Process"
            fila = df[(df['Order'] == int(id_seleccionado))]
                
            if not fila.empty:
                Order_text.set(fila['Order'].iloc[0])
                line_text.set(fila['Line'].iloc[0])
                pn_text.set(fila['PN'].iloc[0])
                date_text.set(fila['Date'].iloc[0])
                turno_text.set(fila['Turno'].iloc[0])
                status_text.set(fila['Status'].iloc[0])
            else:
                # Si no hay filas que cumplan los criterios, puedes establecer los campos de texto en blanco o mostrar un mensaje de error.
                Order_text.set('')
                line_text.set('')
                pn_text.set('')
                date_text.set('')
                turno_text.set('')
                status_text.set('')
        else:
            # Si no se ha seleccionado ningún valor, puedes establecer los campos de texto en blanco o mostrar un mensaje de error.
            Order_text.set('')
            line_text.set('')
            pn_text.set('')
            date_text.set('')
            turno_text.set('')
            status_text.set('')

    # Llamar a la función mostrar_datos() al inicio para mostrar los datos del primer número en la lista desplegable
    mostrar_datos()

    # Llamar a la función mostrar_datos() cuando cambie el valor seleccionado en la barra desplegable
    selected_Order.trace('w', mostrar_datos)
    header_frame.pack()


warnings.filterwarnings("ignore", category=UserWarning, module="customtkinter")
desired_width = 50  # Cambia este valor según tu necesidad
desired_height = 50  # Cambia este valor según tu necesidad

image_path = "apagado.ico"
image = Image.open(image_path)
image = image.resize((desired_width, desired_height))
shutdown_icon = ImageTk.PhotoImage(image)

# Crear el botón de apagado con el icono
shutdown_button = tk.Button(
    master=app,
    image=shutdown_icon,
    command=shutdown_system,
    borderwidth=0,  # para que no tenga borde
    bg='black'  # puedes ajustar el color de fondo según tus necesidades
)


# Posicionar el botón en la esquina superior derecha
shutdown_button.place(relx=0.97, rely=0.03, anchor=tk.NE)

# Use CTkButton instead of tkinter Button
button = customtkinter.CTkButton(master=app, text="Start Order", command=start_program, width=350, height=125, fg_color="green", font=custom_font)
button.place(relx=0.15, rely=0.40, anchor=customtkinter.SW)

Stopbtn = customtkinter.CTkButton(master=app, text="Pause Order", command=stop_program, width=350, height=125, fg_color="red", font=custom_font)
Stopbtn.place(relx = 0.53, rely=0.40, anchor=customtkinter.SW)

Finalbtn = customtkinter.CTkButton(master=app, text="Complete", command=complete_program, width=175, height=62.5, fg_color="Orange", font=custom_font)
Finalbtn.place(relx = 0.89, rely=0.95, anchor=customtkinter.SE)

# Crear el botón para cambiar entre cámaras
CameraBtn = customtkinter.CTkButton(master=app, text=camera_state, command=toggle_camera_text, width=175, height=62.5, fg_color="Blue", font=custom_font)
CameraBtn.place(relx = 0.35, rely=0.95, anchor=customtkinter.SE)

# Funcion para ver la camara
ViewCameraBtn = customtkinter.CTkButton(master=app, text=view_camera_state, command=view_camera, width=175, height=62.5, fg_color="Purple", font=custom_font)
ViewCameraBtn.place(relx=0.66, rely=0.95, anchor=customtkinter.SE)

header()
table_frame.place(relx=0.5, rely=0.62, anchor=tk.CENTER)
insert_table()

# Cargar el archivo de datos en un DataFrame
app.mainloop()
