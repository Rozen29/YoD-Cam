from flask import Flask, render_template, Response, jsonify, request
import cv2
from ultralytics import YOLO
import random
import threading
import time
import numpy as np
import av
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiohttp import web
import json
import asyncio
import os
from datetime import datetime
from collections import deque

# --- Konfigurasi ---
MODEL_NAME = 'yolov8n.pt'
CONFIDENCE_THRESHOLD = 0.4
# PROCESSING_WIDTH = 320 # Opsional, jika ingin resize untuk CPU
# PROCESSING_HEIGHT = 240
TARGET_PROCESSING_FPS_BACKEND = 30 # FPS untuk backend processing, bukan display MJPEG
FORCE_CPU = True # Set True jika tidak ada GPU atau ingin paksa CPU

# Inisialisasi Flask App
app = Flask(__name__)

# Global variables
yolo_model = None
camera = None
camera_active = False
output_frame = None # Frame yang akan di-stream, sudah dengan anotasi
frame_lock = threading.Lock() # Untuk sinkronisasi akses ke output_frame
yolo_thread = None
object_detection_enabled = True # Flag untuk mode deteksi
recording = False
video_writer = None
last_recorded_file = None

# Buffer untuk WebRTC (misal buffer 30 frame = 3 detik @10 FPS)
webrtc_frame_buffer = deque(maxlen=30)

# --- WebRTC/aiortc Integration ---
class YoloVideoStreamTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.last_frame_time = 0
        self.target_interval = 1/10  # 10 FPS
    async def recv(self):
        global webrtc_frame_buffer
        # Ambil frame terbaru dari buffer
        while True:
            if webrtc_frame_buffer:
                frame = webrtc_frame_buffer[-1].copy()
                break
            await asyncio.sleep(0.01)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_frame = av.VideoFrame.from_ndarray(rgb_frame, format="rgb24")
        now = time.time()
        video_frame.pts = int(now * 90000)
        video_frame.time_base = av.Rational(1, 90000)
        # Jaga FPS tetap stabil
        elapsed = time.time() - self.last_frame_time
        if elapsed < self.target_interval:
            await asyncio.sleep(self.target_interval - elapsed)
        self.last_frame_time = time.time()
        return video_frame

async def webrtc_index(request):
    with open('templates/webrtc.html', 'r') as f:
        return web.Response(content_type='text/html', text=f.read())

async def webrtc_offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])
    pc = RTCPeerConnection()
    webrtc_pcs.add(pc)
    video_track = YoloVideoStreamTrack()
    pc.addTrack(video_track)
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    # Return dict, not string, to avoid double encoding and direction error
    return web.json_response({
        'sdp': pc.localDescription.sdp,
        'type': pc.localDescription.type
    })

webrtc_pcs = set()

async def webrtc_on_shutdown(app):
    coros = [pc.close() for pc in webrtc_pcs]
    await asyncio.gather(*coros)
    webrtc_pcs.clear()

def run_webrtc_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = web.Application()
    app.on_shutdown.append(webrtc_on_shutdown)
    app.router.add_get('/webrtc', webrtc_index)
    app.router.add_post('/offer', webrtc_offer)
    web.run_app(app, port=8081, handle_signals=False)

# Jalankan server WebRTC di thread terpisah saat Flask start
webrtc_thread = threading.Thread(target=run_webrtc_server, daemon=True)
webrtc_thread.start()

# --- Fungsi Helper YOLO ---
track_colors_global = {}
class_names_global = {}

def initialize_yolo():
    global yolo_model, class_names_global
    try:
        device = 'cpu' if FORCE_CPU else None
        yolo_model = YOLO(MODEL_NAME)
        if device: # Jika device dispesifikasikan (e.g., 'cpu')
             yolo_model.to(device) # Pindahkan model ke device
        class_names_global = yolo_model.names
        print(f"Model YOLO '{MODEL_NAME}' berhasil dimuat di device: {yolo_model.device}.")
        print(f"Target processing FPS backend: {TARGET_PROCESSING_FPS_BACKEND}")
    except Exception as e:
        print(f"Error saat memuat model YOLO: {e}")
        yolo_model = None

def yolo_processing_loop():
    global camera, output_frame, camera_active, track_colors_global, class_names_global, object_detection_enabled, recording, video_writer, webrtc_frame_buffer

    if yolo_model is None:
        print("Model YOLO tidak terinisialisasi. Loop tidak berjalan.")
        camera_active = False # Pastikan loop tidak dianggap aktif
        return

    source_fps = camera.get(cv2.CAP_PROP_FPS)
    if source_fps == 0: source_fps = 30 # Asumsi untuk webcam
    
    frames_to_skip_interval = max(1, round(source_fps / TARGET_PROCESSING_FPS_BACKEND))
    print(f"Backend: Source FPS: {source_fps:.2f}, Skip Interval: {frames_to_skip_interval}")
    
    frame_count = 0
    last_processed_time = time.time()

    while camera_active and camera.isOpened():
        success, frame = camera.read()
        if not success:
            print("Gagal membaca frame dari kamera.")
            time.sleep(0.01) # Tunggu sebentar sebelum mencoba lagi
            continue

        frame_count += 1
        
        if object_detection_enabled:
            # Frame skipping untuk backend processing
            if frame_count % frames_to_skip_interval == 0:
                current_time = time.time()
                last_processed_time = current_time
                
                frame_to_process = frame.copy()

                try:
                    results = yolo_model.track(frame_to_process, persist=True, conf=CONFIDENCE_THRESHOLD, verbose=False)
                    
                    annotated_frame = frame_to_process # Gambar di frame yg mungkin sdh diresize atau frame asli
                    
                    if results[0].boxes is not None and results[0].boxes.id is not None:
                        boxes_model_res = results[0].boxes.xyxy.cpu().numpy()
                        track_ids = results[0].boxes.id.cpu().numpy().astype(int)
                        class_ids = results[0].boxes.cls.cpu().numpy().astype(int)
                        confidences = results[0].boxes.conf.cpu().numpy()

                        for box_model, track_id, class_id, conf in zip(boxes_model_res, track_ids, class_ids, confidences):
                            x1, y1, x2, y2 = map(int, box_model)

                            if track_id not in track_colors_global:
                                track_colors_global[track_id] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                            color = track_colors_global[track_id]
                            
                            class_name = class_names_global.get(class_id, f"Unknown({class_id})")
                            label = f"ID:{track_id} {class_name} {conf:.2f}"

                            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                            (lw, lh), base = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                            cv2.rectangle(annotated_frame, (x1, y1 - lh - base), (x1 + lw, y1), color, -1)
                            cv2.putText(annotated_frame, label, (x1, y1 - base // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
                    
                    # Update output_frame yang akan di-stream
                    with frame_lock:
                        output_frame = annotated_frame.copy()
                        if recording and video_writer is not None:
                            video_writer.write(annotated_frame)

                except Exception as e:
                    print(f"Error saat YOLO tracking: {e}")
                    with frame_lock: # Jika error, stream frame asli tanpa anotasi
                        output_frame = frame.copy()
                        if recording and video_writer is not None:
                            video_writer.write(frame)
            else:
                if output_frame is None: # Jika belum ada frame yg diproses
                     with frame_lock:
                        output_frame = frame.copy()
                        if recording and video_writer is not None:
                            video_writer.write(frame)
                pass
        else:
            # Live preview only, tanpa deteksi/annotasi
            with frame_lock:
                output_frame = frame.copy()
                if recording and video_writer is not None:
                    video_writer.write(frame)

        # Setelah update output_frame, tambahkan ke buffer WebRTC
        with frame_lock:
            if output_frame is not None:
                webrtc_frame_buffer.append(output_frame.copy())

        time.sleep(0.005) # Optimasi: jeda lebih kecil untuk responsif

    if camera:
        camera.release()
    print("YOLO processing loop finished.")


def generate_frames_for_stream():
    global output_frame
    while camera_active:
        with frame_lock:
            if output_frame is None:
                # Buat frame placeholder jika belum ada
                placeholder = cv2.imread('static/placeholder.png') # Buat gambar placeholder.png di static
                if placeholder is None: # Fallback jika placeholder.png tidak ada
                    placeholder_img = np.zeros((240, 320, 3), dtype=np.uint8)
                    placeholder = cv2.imencode('.jpg', placeholder_img)[1].tobytes()
                    encoded_frame = placeholder
                else:
                    (flag, encoded_image) = cv2.imencode(".jpg", placeholder)
                    if not flag: continue
                    encoded_frame = encoded_image.tobytes()

                time.sleep(0.1) # Tunggu frame pertama
            else:
                (flag, encoded_image) = cv2.imencode(".jpg", output_frame)
                if not flag:
                    print("Gagal encode frame ke JPG")
                    continue
                encoded_frame = encoded_image.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + encoded_frame + b'\r\n')
        time.sleep(1 / 30) # Target FPS untuk streaming MJPEG ke client (misal 30 FPS)

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/list_cameras')
def list_cameras_route():
    available_cameras = []
    index = 0
    max_cameras_to_check = 10 # Increase to check more cameras
    checked_indexes = set()
    while index < max_cameras_to_check:
        cap_test = cv2.VideoCapture(index)
        if cap_test.isOpened():
            available_cameras.append({"id": index, "name": f"Kamera {index}"})
            cap_test.release()
        checked_indexes.add(index)
        index += 1
    # Re-check for new cameras by probing indexes up to max_cameras_to_check
    # This ensures that if a new camera is plugged in, it will be detected on refresh
    return jsonify(available_cameras)

@app.route('/start_camera', methods=['POST'])
def start_camera_route():
    global camera, camera_active, yolo_thread, output_frame

    if camera_active:
        return jsonify({"status": "already_started", "error": "Kamera sudah aktif."}), 400

    data = request.get_json()
    camera_id = data.get('camera_id', 0)

    # Reset output_frame dan track_colors
    with frame_lock:
        output_frame = None
    track_colors_global.clear()

    # Coba buka dengan CAP_DSHOW dulu untuk Windows, lalu fallback
    camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    if not camera.isOpened():
        camera = cv2.VideoCapture(camera_id) # Fallback tanpa CAP_DSHOW
        if not camera.isOpened():
            return jsonify({"status": "error", "error": f"Tidak bisa membuka kamera ID {camera_id}"}), 400

    camera_active = True
    yolo_thread = threading.Thread(target=yolo_processing_loop, daemon=True)
    yolo_thread.start()
    print(f"Kamera ID {camera_id} dimulai.")
    return jsonify({"status": "started"})

@app.route('/stop_camera', methods=['POST'])
def stop_camera_route():
    global camera_active, camera, yolo_thread

    if not camera_active:
        return jsonify({"status": "already_stopped", "error": "Kamera sudah mati."}), 400

    camera_active = False # Signal thread untuk berhenti
    if yolo_thread and yolo_thread.is_alive():
        print("Menunggu YOLO thread untuk berhenti...")
        yolo_thread.join(timeout=5) # Tunggu thread selesai, dengan timeout
        if yolo_thread.is_alive():
            print("YOLO thread tidak berhenti tepat waktu.")
    
    # camera object akan di-release di dalam yolo_processing_loop
    # atau jika loop tidak jalan, pastikan di-release di sini
    if camera and camera.isOpened():
        camera.release()
        camera = None

    print("Kamera dihentikan.")
    return jsonify({"status": "stopped"})

@app.route('/video_feed')
def video_feed_route():
    if not camera_active:
        return "Kamera tidak aktif.", 404 # Atau redirect ke placeholder
    return Response(generate_frames_for_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle_detection', methods=['POST'])
def toggle_detection_route():
    global object_detection_enabled
    data = request.get_json()
    enable = data.get('enable', True)
    object_detection_enabled = bool(enable)
    return jsonify({'status': 'ok', 'object_detection_enabled': object_detection_enabled})

@app.route('/toggle_preview', methods=['POST'])
def toggle_preview_route():
    global object_detection_enabled
    object_detection_enabled = False
    return jsonify({'status': 'ok', 'object_detection_enabled': object_detection_enabled})

@app.route('/start_recording', methods=['POST'])
def start_recording_route():
    global recording, video_writer, last_recorded_file
    if recording:
        return jsonify({'status': 'already_recording'})
    if not camera_active:
        return jsonify({'status': 'error', 'error': 'Kamera belum aktif'}), 400
    os.makedirs('recording', exist_ok=True)
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'recording/record_{now}.mp4'
    last_recorded_file = filename
    # Ambil resolusi dari output_frame atau fallback
    with frame_lock:
        if output_frame is not None:
            height, width = output_frame.shape[:2]
        else:
            width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(filename, fourcc, 15, (width, height))
    recording = True
    return jsonify({'status': 'recording', 'filename': filename})

@app.route('/stop_recording', methods=['POST'])
def stop_recording_route():
    global recording, video_writer
    if not recording:
        return jsonify({'status': 'not_recording'})
    recording = False
    if video_writer is not None:
        video_writer.release()
        video_writer = None
    return jsonify({'status': 'stopped', 'filename': last_recorded_file})

@app.route('/play_recording')
def play_recording_route():
    global last_recorded_file
    if not last_recorded_file or not os.path.exists(last_recorded_file):
        return 'No recording found.', 404
    return Response(
        open(last_recorded_file, 'rb'),
        mimetype='video/mp4',
        headers={'Content-Disposition': f'inline; filename="{os.path.basename(last_recorded_file)}"'}
    )

if __name__ == '__main__':
    initialize_yolo() # Muat model YOLO saat aplikasi dimulai
    if yolo_model:
        # app.run(debug=True, host='0.0.0.0', port=5000, threaded=True) # Debug=True tidak disarankan untuk produksi
        app.run(host='0.0.0.0', port=5000, threaded=True)
    else:
        print("Tidak bisa menjalankan aplikasi karena model YOLO gagal dimuat.")