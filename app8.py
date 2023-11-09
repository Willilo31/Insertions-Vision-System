import cv2
from ultralytics import YOLO
import numpy as np 
import time
import subprocess
from datetime import datetime
import os 
import pandas as pd
import threading
from PIL import Image, ImageDraw, ImageFont
import argparse
import Jetson.GPIO as GPIO
import variable

PINGREEN = 11

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 live")
    parser.add_argument("--webcam-resolution", default=[1280, 720], nargs=2, type=int)
    return parser.parse_args()


def write_to_csv(order_number, item, model, defect_type, time_val, date_val):
    file_path = os.path.join('historial de inserciones', f"{order_number}.csv")
    with open(file_path, 'a') as file:
        file.write(f"{item},{model},{defect_type},{time_val},{date_val}\n")

def save_image_with_timestamp(frame, folder_path, item_number):

    # Convertir el frame de OpenCV a una imagen de PIL
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # Obtener el contexto de dibujo
    draw = ImageDraw.Draw(image)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font = ImageFont.truetype(font_path, 25)  
    
    # Obtener la hora y fecha actuales
    current_time = datetime.now().strftime('%H:%M:%S')
    current_date = datetime.now().strftime('%m/%d/%Y')
    
    # Dibujar la hora y fecha en la imagen
    draw.text((10, 10), f"Time: {current_time}", font=font, fill="black")
    draw.text((10, 50), f"Date: {current_date}", font=font, fill="black")
    
    # Guardar la imagen con el nombre de item_number
    image.save(os.path.join(folder_path, f"{item_number}.png"))

def set_camera_parameters():
    commands = [
        "v4l2-ctl -d /dev/video0 -c focus_auto=0",
        "v4l2-ctl -d /dev/video0 -c focus_absolute=20",
        "v4l2-ctl -d /dev/video0 -c zoom_absolute=100",
    ]
    for command in commands:
        subprocess.run(command, shell=True)

def main(order_number=None, callback=None):
    # args = parse_arguments()
    # frame_width, frame_height = args.webcam_resolution
    cap = cv2.VideoCapture("Product1.webm")
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height) 


    # set_camera_parameters()
    update_table_event = threading.Event()

    model = YOLO("insertionsM01.pt")
    
    class_names = ['Lewer-G', 'Lewer-NG', 'Ysite-G', 'Ysite-NG']
    class_names2 = ['Lower', 'Lower', 'Y-site', 'Y-site']

    line_distance_up = 75
    line_distance_down = 125
    center_y_anterior = 0

    data_matrix = np.empty((0, 17), dtype=int)
    update_matrix = 1
    start_time = time.time()
    frame_count = 0
    prediction = 0
    insertions = ''
    fps = 0.0
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(PINGREEN, GPIO.OUT)
    GPIO.output(PINGREEN, False)
    GPIO.cleanup()

    while True:
        ret, frame = cap.read()
        height, width, _ = frame.shape
        
        if not ret:
            continue

        results = model.track(frame, persist=True, verbose=None, agnostic_nms=True)

        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            class_ids = results[0].boxes.cls.cpu().numpy().astype(int)
            ids = results[0].boxes.id.cpu().numpy().astype(int)

            for box, id, class_id in zip(boxes, ids, class_ids):
                #print(box, id, class_id)
                x1, y1, x2, y2 = box

                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                #cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1) 

                if class_id == 1 or class_id == 3:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 220), 4)  #Rojo  
                    cv2.putText(frame, f"ID: {id} {class_names[class_id]}",(x1-30, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 220), 2,)
                
                if class_id == 0 or class_id == 2:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 4)  #Verde
                    cv2.putText(frame, f"ID: {id} {class_names[class_id]}",(x1-30, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 0), 2,)
                    
                if line_distance_up < center_y < (height - line_distance_down):
                    if class_id == 3 or class_id == 1:
                        tracker_exists = False
                        for i in range (data_matrix.shape[0]):
                            if data_matrix[i, 0] == id:
                                if data_matrix[i, -1] != 0:
                                    data_matrix[i, 1:-1] = data_matrix[i, 2:] 
                                    data_matrix[i, -1] = 0
                                    update_matrix = 0
                                data_matrix[i, np.count_nonzero(data_matrix[i]) + update_matrix] = class_id
                                update_matrix = 1
                                tracker_exists = True
                                break

                        if not tracker_exists:
                            if isinstance(id, np.int64):
                                new_row = np.zeros(data_matrix.shape[1], dtype=int)
                                new_row[0] = id
                                new_row[1] = class_id
                                data_matrix = np.vstack((data_matrix, new_row))
                    print(data_matrix)

                if (height - line_distance_down) < center_y:
                    
                    row_to_analyze = np.where(data_matrix[:, 0] == id)[0]
                    vector = data_matrix[row_to_analyze, :]

                    current_time = datetime.now().strftime('%H:%M:%S')
                    current_date = datetime.now().strftime('%m/%d/%Y')
                    
                    if vector.size > 0:
                        prediction = np.argmax(np.bincount(vector.flatten()))
                        print(class_names[prediction])
                        if prediction == 1 or prediction == 3:
                            # GPIO.cleanup()
                            subprocess.Popen(["python3", "RedLight.py"])
                            file_path = os.path.join('historial de inserciones', f"{order_number}.csv")
                            df = pd.read_csv(file_path)
                            
                            if not df.empty:
                                last_item = df['Item'].iloc[-1]
                                next_item = last_item + 1
                            else:
                                next_item = 1

                            if prediction == 1 or prediction == 3:
                                insertions = 'Bad insertion'

                            write_to_csv(order_number, next_item, class_names2[prediction],insertions, current_time, current_date)
                            update_table_event.set() 

                            # Crear la carpeta photo_history si no existe
                            if not os.path.exists('photo_history'):
                                os.mkdir('photo_history')

                            # Crear la carpeta con el nombre del order_number si no existe
                            order_folder_path = os.path.join('photo_history', order_number)
                            if not os.path.exists(order_folder_path):
                                os.mkdir(order_folder_path)
                            
                            # Guardar la imagen con la hora, fecha y nombre del ítem
                            #cv2.circle(frame, (center_x, center_y), 50, (0, 0, 255),7) 
                            save_image_with_timestamp(frame, order_folder_path, next_item)
                            if callback:
                                callback()
                    data_matrix = np.delete(data_matrix, row_to_analyze, axis=0)

        #Fps
        frame_count += 1
        elapsed_time = time.time() - start_time
        if elapsed_time > 1.0:
            fps = frame_count / elapsed_time
            start_time = time.time()
            frame_count = 0

        cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.line(frame, (0, line_distance_up), (width, line_distance_up), (0, 0, 255), 2)
        cv2.line(frame, (0, height - line_distance_down), (width, height - line_distance_down), (0, 0, 255), 2)
        
        if variable.VIEWCAMARA[0] == 1:
            cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
            # cv2.resizeWindow('frame', 450,450)
            cv2.imshow("frame", frame)

        if variable.VIEWCAMARA[0] == 0:
            cv2.destroyAllWindows()

        if (cv2.waitKey(30) == 27 or variable.STOPSYSTEM[0] == 1):
            cv2.destroyAllWindows()
            break

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PINGREEN, GPIO.OUT)
    GPIO.output(PINGREEN, True)
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()

if __name__ == "__main__":
    main()
