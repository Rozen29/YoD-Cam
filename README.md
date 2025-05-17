# ✨ YOLOv8 Web Detector - Pemantauan & Peringatan Real-Time ✨

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Aplikasi web canggih yang memanfaatkan kekuatan YOLOv8 untuk deteksi objek secara _real-time_ melalui kamera lokal. Dilengkapi dengan streaming MJPEG & WebRTC, perekaman, autentikasi pengguna, fitur upload media untuk analisis, dan **integrasi peringatan WhatsApp** untuk pemantauan proaktif.

<!--
💡 **Pro Tip:** Tambahkan GIF demo aplikasi di sini untuk visualisasi yang lebih baik!
Contoh: <p align="center"><img src="link_ke_demo.gif" alt="YOLO Web Detector Demo" width="700"></p>
-->

## 🚀 Fitur Unggulan

*   👁️ **Deteksi & Pelacakan Objek Real-Time:** Menggunakan model YOLOv8 dari Ultralytics untuk identifikasi dan pelacakan objek yang akurat.
*   🔐 **Autentikasi Pengguna:** Sistem login berbasis username/password sederhana dengan proteksi _brute-force_ (batas percobaan & cooldown).
*   📱 **Peringatan WhatsApp Terintegrasi:** Menerima notifikasi WhatsApp secara _real-time_ jika objek tertentu (misal, 'person', 'car') terdeteksi melebihi durasi yang ditetapkan. (Memerlukan layanan Node.js terpisah).
*   🎥 **Mode Streaming Ganda:**
    *   **MJPEG:** Kompatibilitas tinggi di berbagai browser (via Flask).
    *   **WebRTC:** Latensi sangat rendah, ideal untuk responsivitas (via aiortc + aiohttp).
*   ⚙️ **Kontrol Kamera & Deteksi Interaktif:**
    *   Pilih sumber kamera yang tersedia.
    *   Mulai/Hentikan streaming kamera.
    *   Aktifkan/Nonaktifkan deteksi objek secara dinamis.
    *   Beralih ke mode Live Preview (hanya video tanpa deteksi).
*   ⏺️ **Rekam & Putar Ulang:** Simpan sesi video (dengan anotasi deteksi) ke file MP4 dan putar kembali langsung dari antarmuka web.
*   📤 **Upload & Analisis Media:** Unggah file gambar atau video untuk diproses dengan deteksi YOLOv8 dan lihat hasilnya.
*   🖥️ **Antarmuka Web Modern & Responsif:** Dibangun dengan HTML, CSS, dan JavaScript vanilla untuk kemudahan penggunaan.

## 📂 Struktur Proyek

```bash

├── app.py                # Aplikasi Flask utama: API, MJPEG, integrasi WebRTC, logika deteksi & peringatan
├── node.js               # (Opsional) Layanan Node.js untuk mengirim pesan WhatsApp via whatsapp-web.js
├── .env                  # File konfigurasi untuk kredensial, nomor WhatsApp, dll. (JANGAN DI-COMMIT)
├── requirements.txt      # Daftar dependensi Python
├── package.json          # (Opsional) Dependensi untuk layanan Node.js
├── yolov8n.pt            # Model YOLOv8 default (akan diunduh otomatis jika belum ada)
├── recording/            # Folder untuk menyimpan hasil rekaman video MP4
├── wwebjs_auth/          # (Opsional) Folder untuk menyimpan sesi autentikasi whatsapp-web.js
├── static/
│   └── placeholder.png   # Gambar placeholder untuk stream video
│   └── (style.css)       # (Opsional) File CSS kustom
└── templates/
    ├── index.html        # Halaman utama aplikasi (streaming, kontrol, upload)
    └── login.html        # Halaman login pengguna

```

## 🛠️ Instalasi

**Prasyarat:**
*   Python 3.8+
*   `pip` (Python package installer)
*   (Opsional) Node.js dan `npm` jika menggunakan fitur peringatan WhatsApp.
*   Kamera webcam atau USB yang terhubung.

**Langkah-langkah:**

1.  **Clone Repositori:**
    ```bash
    git clone <URL_REPO_ANDA>
    cd <NAMA_FOLDER_PROYEK>
    ```

2.  **(Sangat Direkomendasikan) Buat dan Aktifkan Virtual Environment Python:**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependensi Python:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Siapkan File `.env`:**
    Buat file bernama `.env` di direktori root proyek dan isi dengan konfigurasi berikut (sesuaikan nilainya):
    ```ini
    FLASK_SECRET_KEY=kunci_rahasia_flask_anda_yang_sangat_panjang
    FLASK_USERNAME=admin
    FLASK_PASSWORD=password123
    NODE_SERVICE_URL=http://localhost:3000/send-message # Sesuaikan port jika node.js berjalan di port lain
    WHATSAPP_TARGET_NUMBER=6281234567890 # Nomor WA tujuan dengan kode negara (tanpa '+')
    ```
    **PENTING:** Jangan pernah commit file `.env` Anda ke repositori Git publik. Tambahkan `.env` ke file `.gitignore` Anda.

5.  **(Opsional) Setup Layanan Notifikasi WhatsApp (Node.js):**
    Jika Anda ingin menggunakan fitur peringatan WhatsApp:
    *   Pastikan Node.js dan npm terinstal.
    *   Dari direktori root proyek, jalankan:
        ```bash
        npm install
        ```
    *   Layanan Node.js biasanya akan menggunakan port 3000 (sesuai `NODE_SERVICE_URL` di atas). Anda bisa mengubah port di `node.js` jika diperlukan.

6.  **Model YOLOv8:**
    *   File model `yolov8n.pt` (atau model lain yang Anda konfigurasi di `MODEL_NAME` dalam `app.py`) akan diunduh secara otomatis oleh `ultralytics` saat pertama kali `initialize_yolo()` dipanggil jika belum ada.

## ▶️ Menjalankan Aplikasi

1.  **Pastikan Anda berada di direktori root proyek** dan virtual environment Python (jika digunakan) sudah aktif.

2.  **(Opsional) Jalankan Layanan Notifikasi WhatsApp:**
    Jika menggunakan peringatan WhatsApp, buka terminal baru, navigasi ke root proyek, dan jalankan:
    ```bash
    npm start
    ```
    Anda mungkin perlu memindai kode QR dengan aplikasi WhatsApp Anda untuk pertama kalinya untuk menghubungkan perangkat. Folder `wwebjs_auth/` akan dibuat untuk menyimpan sesi.

3.  **Jalankan Server Aplikasi Flask:**
    Di terminal utama Anda (dengan virtual environment Python aktif):
    ```bash
    python app.py
    ```
    Server Flask akan berjalan di `http://localhost:5000` dan server WebRTC (aiohttp) akan berjalan di `http://localhost:8081` (port-port ini bisa dikonfigurasi).

4.  **Akses Antarmuka Web:**
    Buka browser favorit Anda dan kunjungi:
    *   `http://localhost:5000/`
    Anda akan diarahkan ke halaman login. Gunakan kredensial dari file `.env` Anda.

## 🎮 Fitur Antarmuka Web

Setelah login, Anda dapat:

*   🔑 **Logout:** Keluar dari sesi Anda.
*   🌐 **Pilih Kamera:** Pilih dari daftar device webcam yang terdeteksi.
*   🎬 **Start/Stop Kamera:** Memulai atau menghentikan streaming video.
*   🤖 **Deteksi: ON/OFF:** Mengaktifkan atau menonaktifkan fitur deteksi objek.
*   🖼️ **Live Preview Only:** Beralih ke mode pratinjau langsung tanpa pemrosesan deteksi.
*   🔴 **Mulai Rekam / Stop Rekam:** Merekam output video (dengan overlay deteksi) ke file MP4.
*   📼 **Putar Rekaman Terakhir:** Setelah rekaman dihentikan, tautan untuk memutar file akan muncul.
*   ⬆️ **Upload & Track:** Unggah file gambar atau video untuk dianalisis oleh YOLOv8. Hasilnya akan ditampilkan di bawah form upload.

## 💡 Catatan Teknis

*   **Peringatan WhatsApp:** Jika objek yang dikonfigurasi (misal, 'person') terdeteksi secara terus-menerus selama lebih dari `ALERT_DURATION_THRESHOLD` (default 10 detik), aplikasi Flask akan mengirim permintaan ke layanan Node.js, yang kemudian akan mengirim pesan WhatsApp ke `WHATSAPP_TARGET_NUMBER`. Ada periode `ALERT_COOLDOWN_PERIOD` untuk mencegah spam dari ID objek yang sama.
*   **MJPEG & WebRTC:** Pilih mode streaming yang sesuai dengan kebutuhan Anda. WebRTC menawarkan latensi lebih rendah.
*   **Model YOLO:** Aplikasi menggunakan `yolov8n.pt` secara default. Anda dapat mengubahnya di `app.py` ke varian lain (misal, `yolov8s.pt` untuk akurasi lebih baik dengan biaya performa) atau model kustom.
*   **Konfigurasi Performa:** `CONFIDENCE_THRESHOLD`, `TARGET_PROCESSING_FPS_BACKEND`, dan `TRACK_TIMEOUT_SECONDS` di `app.py` dapat disesuaikan untuk menyeimbangkan akurasi dan performa.

## 📋 Kebutuhan Sistem

*   Python 3.8 atau versi lebih baru.
*   (Opsional) Node.js versi LTS terbaru.
*   Webcam/USB camera yang berfungsi, atau sumber video RTSP yang valid.
*   Sistem Operasi: Linux, Windows, atau macOS.

## 🆘 Troubleshooting

*   **Error `requests.exceptions.ConnectionError` saat mengirim WhatsApp:** Pastikan layanan Node.js (`node.js`) berjalan dan dapat diakses di URL dan port yang dikonfigurasi dalam `NODE_SERVICE_URL` di file `.env`.
*   **Tidak ada peringatan WhatsApp terkirim:**
    *   Cek apakah layanan Node.js terautentikasi dengan WhatsApp (lihat output konsol Node.js).
    *   Verifikasi `WHATSAPP_TARGET_NUMBER` di `.env`.
    *   Perhatikan log di konsol Flask untuk melihat apakah kondisi peringatan terpenuhi dan apakah ada error saat mengirim permintaan ke layanan Node.js.
*   **Objek terdeteksi sebentar lalu hilang:** Coba sesuaikan `CONFIDENCE_THRESHOLD` (mungkin perlu diturunkan sedikit) dan `TRACK_TIMEOUT_SECONDS` (mungkin perlu dinaikkan sedikit) di `app.py`.
*   **Error WebRTC terkait thread:** Pastikan `handle_signals=False` saat menjalankan `web.run_app` di `app.py`.
*   **Video patah-patah:** Coba gunakan mode WebRTC atau turunkan `TARGET_PROCESSING_FPS_BACKEND`.
*   **Tidak ada kamera terdeteksi:** Periksa koneksi, izin, dan driver kamera. Pastikan tidak ada aplikasi lain yang menggunakan kamera.

## 📜 Lisensi

Proyek ini dilisensikan di bawah [Lisensi MIT](https://opensource.org/licenses/MIT).

---

**Dibuat dengan ❤️ oleh Rozen 2025**