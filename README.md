# ✨ YOLO Web Detector & Streaming ✨

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Bawa kemampuan deteksi objek _real-time_ canggih dengan YOLOv8 langsung ke browser Anda! Aplikasi web ini dirancang untuk memonitor kamera lokal maupun jaringan, dengan dukungan streaming MJPEG (untuk kompatibilitas luas) dan WebRTC (untuk latensi super rendah). Rekam hasil deteksi dan putar ulang kapan saja.

<!--
💡 **Pro Tip:** Tambahkan GIF demo aplikasi di sini untuk visualisasi yang lebih baik!
Contoh: <p align="center"><img src="link_ke_demo.gif" alt="YOLO Web Detector Demo" width="700"></p>
-->

## 🚀 Fitur Utama

*   👁️ **Deteksi Objek Real-Time:** Didukung oleh model YOLOv8 dari Ultralytics.
*   🎥 **Mode Streaming Ganda:**
    *   **MJPEG:** Kompatibilitas tinggi di berbagai browser (via Flask).
    *   **WebRTC:** Latensi rendah, ideal untuk responsivitas (via aiortc + aiohttp).
*   ⚙️ **Kontrol Interaktif:**
    *   Aktifkan/Nonaktifkan deteksi objek.
    *   Mode Live Preview (hanya menampilkan video tanpa deteksi).
    *   Pilih sumber kamera.
    *   Mulai/Hentikan streaming kamera.
*   ⏺️ **Rekam & Putar Ulang:** Simpan sesi deteksi ke file MP4 dan putar kembali dengan mudah.
*   🖥️ **UI Web Modern:** Antarmuka pengguna yang intuitif dengan tombol kontrol lengkap.

## 📂 Struktur Proyek

├── app.py                # Aplikasi Flask utama: MJPEG, integrasi WebRTC, API
├── webrtc_server.py      # (Opsional) Server demo WebRTC standalone
├── requirements.txt      # Daftar dependensi Python
├── yolov8n.pt            # Model YOLOv8 default (perlu diunduh)
├── recording/            # Folder untuk menyimpan hasil rekaman video MP4
├── static/
│   └── style.css         # File CSS untuk tampilan antarmuka web
└── templates/
    ├── index.html        # Halaman web utama (streaming MJPEG & kontrol)
    └── webrtc.html       # (Opsional) Halaman demo untuk WebRTC standalone


## 🛠️ Instalasi

**Prasyarat:**
*   Python 3.8+
*   `pip` (Python package installer)
*   Kamera webcam atau USB yang terhubung

**Langkah-langkah:**

1.  **Clone Repositori:**
    ```bash
    git https://github.com/Rozen29/YoD-Cam.git
    cd yolo_web_detector
    ```

2.  **(Sangat Direkomendasikan) Buat dan Aktifkan Virtual Environment:**
    ```bash
    python -m venv venv
    # Untuk Windows:
    venv\Scripts\activate
    # Untuk macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependensi:**
    ```bash
    pip install -r requirements.txt
    ```
    Atau, install secara manual:
    ```bash
    pip install flask opencv-python ultralytics aiortc aiohttp av numpy
    ```

4.  **Unduh Model YOLOv8:**
    *   Pastikan file model (default: `yolov8n.pt`) ada di direktori root proyek.
    *   Jika belum ada, Anda bisa mengunduhnya. Cara termudah adalah dengan skrip Python singkat:
        ```python
        # Jalankan skrip ini sekali untuk mengunduh model
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt') # Akan otomatis mengunduh jika belum ada
        print("Model yolov8n.pt berhasil diunduh/diverifikasi.")
        ```
    *   Jika Anda menggunakan model YOLOv8 lain (misal `yolov8s.pt`), ganti nama file model di `app.py`.

## ▶️ Menjalankan Aplikasi

1.  **Pastikan Anda berada di direktori root proyek** dan virtual environment (jika digunakan) sudah aktif.

2.  **Jalankan Server Aplikasi:**
    ```bash
    python app.py
    ```
    Server akan berjalan, mengintegrasikan Flask untuk MJPEG dan aiohttp untuk WebRTC.

3.  **Akses Antarmuka Web:**
    Buka browser favorit Anda dan kunjungi:
    *   `http://localhost:5000/`

## 🎮 Fitur Antarmuka Web

Dari halaman web, Anda dapat:

*   🌐 **Pilih Kamera:** Pilih dari daftar device webcam yang terdeteksi.
*   🎬 **Start/Stop Kamera:** Memulai atau menghentikan streaming video.
*   🤖 **Deteksi: ON/OFF:** Mengaktifkan atau menonaktifkan fitur deteksi objek.
*   🖼️ **Live Preview Only:** Beralih ke mode pratinjau langsung tanpa pemrosesan deteksi.
*   🔴 **Mulai Rekam / Stop Rekam:** Merekam output video (dengan overlay deteksi) ke file MP4.
*   📼 **Putar Rekaman Terakhir:** Setelah rekaman dihentikan, tautan untuk memutar file akan muncul.

## 💡 Catatan Teknis

*   **MJPEG:** Kompatibel secara luas, namun memiliki latensi yang lebih tinggi. Cocok untuk setup sederhana atau browser lama.
*   **WebRTC:** Menawarkan latensi sangat rendah dan penanganan buffer otomatis, menjadikannya ideal untuk jaringan yang kurang stabil atau kebutuhan real-time yang tinggi.
*   **Perekaman:** File video disimpan dalam format MP4 di dalam folder `recording/`.
*   **Model YOLO:** Aplikasi menggunakan `yolov8n.pt` secara default. Anda bisa menggantinya dengan varian lain atau model kustom di `app.py`.
*   **Koneksi Lambat:** WebRTC dirancang untuk menyesuaikan diri dengan kondisi jaringan. FPS juga dapat diatur di kode backend untuk optimalisasi lebih lanjut.

## 📋 Kebutuhan Sistem

*   Python 3.8 atau versi lebih baru.
*   Webcam/USB camera yang berfungsi.
*   Sistem Operasi: Linux, Windows, atau macOS.

## 🆘 Troubleshooting

*   **Error WebRTC terkait thread?** Pastikan `handle_signals=False` saat menjalankan `web.run_app` di `app.py` (jika Anda memodifikasi loop event aiohttp secara manual).
*   **Video patah-patah?** Coba gunakan mode WebRTC. Pastikan juga FPS di backend tidak di-set terlalu tinggi melebihi kemampuan pemrosesan atau bandwidth.
*   **Tidak ada kamera terdeteksi?**
    *   Periksa apakah kamera terhubung dengan benar.
    *   Pastikan aplikasi memiliki izin untuk mengakses kamera.
    *   Cek driver kamera Anda.
    *   Pastikan tidak ada aplikasi lain yang sedang menggunakan kamera secara eksklusif.

## 📜 Lisensi

Proyek ini dilisensikan di bawah [Lisensi MIT](LICENSE). <!-- Jika Anda memiliki file LICENSE, ubah tautan ini ke 'LICENSE' saja -->

---

**Dibuat dengan ❤️ oleh Rozen (2025)**
