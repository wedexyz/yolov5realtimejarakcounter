import cv2
import serial
import time

# --- KONFIGURASI ---
PORT_SERIAL = 'COM9' 
BAUDRATE = 9600
INDEX_KAMERA = 0  # Diubah ke 2 sesuai variabel Anda (sebelumnya Anda hardcode ke 0)
DURASI_REKAM = 5  # Durasi perekaman video dalam detik

# Inisialisasi koneksi Serial ke Arduino
try:
    arduino = serial.Serial(port=PORT_SERIAL, baudrate=BAUDRATE, timeout=0.1)
    time.sleep(2) 
except Exception as e:
    print(f"Gagal membuka port serial: {e}")
    exit()

# Inisialisasi Kamera menggunakan OpenCV
cap = cv2.VideoCapture(INDEX_KAMERA, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Gagal membuka kamera.")
    arduino.close()
    exit()

# Mendapatkan FPS asli kamera untuk kestabilan video output (Default: 30.0 jika gagal)
fps_kamera = cap.get(cv2.CAP_PROP_FPS)
if fps_kamera <= 0:
    fps_kamera = 30.0

# Mengambil resolusi frame dari kamera secara dinamis
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Menggunakan Codec 'XVID' untuk menghasilkan format file .avi
fourcc = cv2.VideoWriter_fourcc(*'XVID')

print("Sistem siap. Tekan 'q' di jendela kamera untuk keluar.")

# --- VARIABEL KONTROL LOOP ---
hitung_video = 0
siap_rekam = True       # Mengizinkan pemicuan rekaman baru
sedang_merekam = False   # Status penanda proses perekaman aktif
waktu_mulai_rekam = 0    # Menyimpan timestamp awal rekaman
video_writer = None     # Object untuk menyimpan file video

try:
    while True:
        # 1. Ambil frame terbaru dari kamera
        ret, frame = cap.read()
        if not ret:
            print("Gagal mengambil gambar dari kamera.")
            break

        # Jika status merekam aktif, tulis frame ke dalam file video
        if sedang_merekam and video_writer is not None:
            video_writer.write(frame)
            # Cek apakah durasi perekaman sudah mencapai batas (3 detik)
            if time.time() - waktu_mulai_rekam >= DURASI_REKAM:
                video_writer.release()
                sedang_merekam = False
                print(f"--> [SUKSES] Video selesai direkam.")

        # 2. Tampilkan stream kamera ke layar (Tetap tampilkan teks indikator saat merekam)
        frame_tampilan = frame.copy()
        if sedang_merekam:
            cv2.putText(frame_tampilan, "REC 3s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Stream Kamera OpenCV", frame_tampilan)

        # 3. Cek apakah ada data masuk dari Arduino
        if arduino.in_waiting > 0:
            try:
                data_masuk = arduino.readline().decode('utf-8').strip()
                
                if data_masuk:
                    print(f"Data dari Arduino: '{data_masuk}'")
                    
                    # Logika: Jika data "FOTO" dan tidak sedang dalam proses merekam video
                    if data_masuk == "FOTO":
                        if siap_rekam and not sedang_merekam:
                            hitung_video += 1
                            nama_file = f"rekaman_arduino_{hitung_video}.avi"
                            
                            # Inisialisasi video writer baru untuk file saat ini
                            video_writer = cv2.VideoWriter(nama_file, fourcc, fps_kamera, (frame_width, frame_height))
                            
                            waktu_mulai_rekam = time.time()
                            sedang_merekam = True
                            siap_rekam = False
                            print(f"--> Memulai perekaman video ke-{hitung_video}: {nama_file}")
                    else:
                        siap_rekam = True
                else:
                    siap_rekam = True
                        
            except UnicodeDecodeError:
                pass
        else:
            # Hanya reset kunci pemicu jika sedang tidak melakukan proses perekaman video
            if not sedang_merekam:
                siap_rekam = True

        # 4. Beri jeda 1ms dan cek jika user menekan tombol 'q' untuk keluar
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Bersihkan sisa rekaman jika aplikasi ditutup paksa saat merekam
    if video_writer is not None and sedang_merekam:
        video_writer.release()
        
    cap.release()
    cv2.destroyAllWindows()
    arduino.close()
