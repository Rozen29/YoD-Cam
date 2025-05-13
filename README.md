<<<<<<< HEAD
# YoD-Cam
=======
# YOLO Web Detector & Streaming

## Deskripsi
Aplikasi ini adalah webapp deteksi objek real-time berbasis YOLOv8 yang dapat diakses melalui browser. Mendukung dua mode streaming: MJPEG (untuk kompatibilitas luas) dan WebRTC (untuk latensi rendah). Hasil deteksi dapat direkam dan diputar ulang. Cocok untuk monitoring kamera lokal maupun jaringan.

## Fitur Utama
- Deteksi objek real-time dengan YOLOv8 (Ultralytics)
- Streaming video MJPEG (via Flask) dan WebRTC (via aiortc + aiohttp)
- On/Off deteksi objek & mode live preview
- Rekam hasil deteksi ke file MP4, putar ulang rekaman
- Pilih kamera, start/stop kamera dari web
- UI web modern, tombol kontrol lengkap

## Struktur Project
```
app.py                # Main Flask app (MJPEG, API, WebRTC integrasi)
webrtc_server.py      # (Opsional) Demo server WebRTC standalone
requirements.txt      # Daftar dependensi Python
recording/            # Folder hasil rekaman video
static/style.css      # CSS untuk UI
templates/index.html  # Halaman utama web (MJPEG)
templates/webrtc.html # Halaman demo WebRTC
```

## Instalasi
1. **Clone repo & install dependencies**
   ```bash
   pip install -r requirements.txt
   # atau manual:
   pip install flask opencv-python ultralytics aiortc aiohttp av numpy
   ```
2. **Download model YOLOv8**
   - Pastikan file `yolov8n.pt` ada di folder project (atau ganti nama di `app.py`)

## Menjalankan Aplikasi
1. **Jalankan Flask + WebRTC**
   ```bash
   python app.py
   ```
2. **Akses web**
   - MJPEG: buka `http://localhost:5000/`

## Fitur Web
- **Pilih Kamera**: Pilih device webcam yang tersedia
- **Start/Stop Kamera**: Mulai/berhenti streaming
- **Deteksi: ON/OFF**: Aktifkan/nonaktifkan deteksi objek
- **Live Preview Only**: Mode tanpa deteksi/tracking
- **Mulai Rekam / Stop Rekam**: Rekam hasil deteksi ke file MP4
- **Putar Rekaman Terakhir**: Tautan muncul setelah stop recording

## Catatan Teknis
- **MJPEG**: Kompatibel di semua browser, latensi lebih tinggi
- **WebRTC**: Latensi rendah, buffer otomatis, cocok untuk jaringan lambat
- **Recording**: File disimpan di folder `recording/`, format MP4
- **YOLO**: Model default `yolov8n.pt`, bisa diganti di `app.py`
- **Koneksi Lambat**: WebRTC otomatis buffer, FPS bisa diatur di kode

## Kebutuhan Sistem
- Python 3.8+
- Webcam/USB camera
- OS: Linux/Windows/Mac

## Troubleshooting
- Jika WebRTC error di thread: pastikan `handle_signals=False` pada `web.run_app`
- Jika video patah-patah: gunakan WebRTC, pastikan FPS backend tidak terlalu tinggi
- Jika tidak ada kamera terdeteksi: cek device, permissions, dan driver

## Lisensi
MIT

---

**By Rozen (2025)**
>>>>>>> 64b6693 (Initial commit: YOLO Web Detector & Streaming)
