import cv2
import os
import numpy as np
import torch
import pandas as pd
# Model
import pathlib
import platform

# Force PosixPath to be compatible with Windows
if platform.system() == 'Windows':
    pathlib.PosixPath = pathlib.WindowsPath

model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt')

# Inisialisasi kamera
cap = cv2.VideoCapture(0)

# Folder untuk simpan gambar
folder = 'saved_images'
folder2 = 'prediksi'
if not os.path.exists(folder):
    os.makedirs(folder)

img_counter = 0

print("Tekan 's' untuk simpan gambar, 'q' untuk keluar.")

while True:
    ret, frame = cap.read()
    ret, image = cap.read()
    detections = model(frame[..., ::-1])
    results = detections.pandas().xyxy[0].to_dict(orient="records")
        
    for result in results:
                    con = result['confidence']
                    #if con > 0.4 :
                    cs  = result['name']
                    x1  = int(result['xmin'])
                    y1  = int(result['ymin'])
                    x2  = int(result['xmax'])
                    y2  = int(result['ymax'])
                    center = int((x1 + x2)/2), int((y1 + y2)/2)
                    ## Menghitung Jarak ##
                    x =int(result['xmin'])
                    y=int(result['ymin'])
                    w= int(result['xmax'])
                    h= int(result['ymax'])
                    eyeradius = w / 20
                    yeye = y + h/3
                    reye = x + (w/2) - (w/5)
                    leye = x + (w/2) + (w/5)
                    space = leye - reye
                    f = 690
                    r = 10
                    distance = f * r / space
                    distance_in_cm = int(distance)
                    if distance_in_cm < 25:
                        #sangat_dekat_count += 1
                        status = "Sangat Dekat"
                        warna = (0, 0, 255) # Merah
                    elif 25 <= distance_in_cm <= 50:
                        #dekat_count += 1
                        status = "Dekat"
                        warna = (0, 165, 255) # Orange
                    elif 51 <= distance_in_cm <= 100:
                        #sedang_count += 1
                        status = "Sedang"
                        warna = (0, 255, 255) # Kuning
                    else:
                        #jauh_count += 1
                        status = "Jauh"
                        warna = (0, 255, 0) # Hijau
                    cv2.putText(frame, str(distance_in_cm) +"cm", (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255),1)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), warna, 2)
                    cv2.putText(frame, str(float(np.around(con, 1))) , (x1+50, y1-5),  cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255), 1)
   
    if not ret:
        break

    # Tampilkan live stream
    cv2.imshow('Camera Feed', frame)
    #cv2.imshow('Camera Feed2', img)
    key = cv2.waitKey(1) & 0xFF

    # 1. Simpan dengan tombol 's'
    if key == ord('s'):
        img_name = 'gbr.png'
        cv2.imwrite(img_name, image)
        img = cv2.imread(img_name)
        detections = model(img)
        results = detections.pandas().xyxy[0].to_dict(orient="records")

         
        sangat_dekat_count = 0  # < 25 cm
        dekat_count = 0         # 25 - 50 cm
        sedang_count = 0        # 51 - 100 cm
        jauh_count = 0          # > 100 cm

        for result in results:
                    con = result['confidence']
                    #if con > 0.4 :
                    cs2  = result['name']
                    xx1  = int(result['xmin'])
                    xy1  = int(result['ymin'])
                    xx2  = int(result['xmax'])
                    xy2  = int(result['ymax'])
                    center = int((x1 + x2)/2), int((y1 + y2)/2)
                    ## Menghitung Jarak ##
                    x2 =int(result['xmin'])
                    y2=int(result['ymin'])
                    w2= int(result['xmax'])
                    h2= int(result['ymax'])
                    eyeradius = w2 / 20
                    yeye = y2 + h2/3
                    reye = x2 + (w2/2) - (w2/5)
                    leye = x2 + (w2/2) + (w2/5)
                    space = leye - reye
                    f = 690
                    r = 10
                    distance = f * r / space
                    distance_in_cm = int(distance)
                   
                    cv2.putText(img, str(distance_in_cm) +"cm", (xx1, xy1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255),1)
                     # 2. Logika Tambah Nilai jika jarak < 20
                    if distance_in_cm < 25:
                        sangat_dekat_count += 1
                        status = "Sangat Dekat"
                        warna = (0, 0, 255) # Merah
                    elif 25 <= distance_in_cm <= 50:
                        dekat_count += 1
                        status = "Dekat"
                        warna = (0, 165, 255) # Orange
                    elif 51 <= distance_in_cm <= 100:
                        sedang_count += 1
                        status = "Sedang"
                        warna = (0, 255, 255) # Kuning
                    else:
                        jauh_count += 1
                        status = "Jauh"
                        warna = (0, 255, 0) # Hijau

                    # Tampilkan Status di dekat objek
                    cv2.putText(img, status, (xx1, xy2 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, warna, 1)
                    cv2.rectangle(img, (xx1, xy1), (xx2, xy2), warna, 2)

        # 3. Menu Dashboard di pojok kiri atas
        bg_color = (0, 0, 0)
        cv2.putText(img, f"S. Dekat (<25cm): {sangat_dekat_count}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(img, f"Dekat (25-50cm): {dekat_count}", (20, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)
        cv2.putText(img, f"Sedang (51-100cm): {sedang_count}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv2.putText(img, f"Jauh (>100cm): {jauh_count}", (20, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                  
        cv2.imshow('YOLOv5 Image Detection', img)
        
        cv2.imwrite(img_name, img)
        print(   sangat_dekat_count , # < 25 cm
        dekat_count ,         # 25 - 50 cm
        sedang_count ,        # 51 - 100 cm
        jauh_count   )
       
        print(f"Gambar disimpan: {img_name}")
        img_counter += 1
        

    # 2. Keluar dengan tombol 'q'
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
