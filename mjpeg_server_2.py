#!/usr/bin/python3

# This is the same as mjpeg_server.py, but uses the h/w MJPEG encoder.

import io
import logging
import socketserver

from http import server
from threading import Condition

from client import client
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder, H264Encoder, Quality
from picamera2.outputs import FileOutput

logging.basicConfig(level=logging.INFO)

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()



camera_running = False
camera = Picamera2()

# stream

stream_clients = set()
stream_output = StreamingOutput()
STREAM_RESOLUTION = (320,240)
RECORD_RESOLUTION = (1280, 720)

# Main configuration for captured videos, lores configuration for stream

video_config = camera.create_video_configuration(
    main={"size": RECORD_RESOLUTION}, 
    lores={"size": STREAM_RESOLUTION})

still_config = camera.create_still_configuration(
    lores={"size": STREAM_RESOLUTION})

camera.configure(video_config)

# minio

bucket = "raspberry"

# encoders

stream_encoder = MJPEGEncoder()


def start_camera():
    global camera_running
    if not camera_running:
        camera.start()
        camera_running = True

def stop_camera():
    global camera_running
    if (len(camera.encoders) < 1):
        camera.stop()
        camera_running = False
        logging.info("Camera stopped.")

def capture_still():
        
    # Start camera, if not started yet
    
    start_camera()
    
    # If recording, pause recording.
    
    video_capture_paused = False
    
    if video_capture.encoder in camera.encoders:
        camera.stop_encoder(encoders=[video_capture.encoder])
        video_capture_paused = True
        logging.info("Recording paused.")
    

    # Configure for high-quality still picture, 
    # take picture and switch back to streaming config
    
    camera.switch_mode(still_config)
    logging.info("Configurated for high quality still image")
    
    data = io.BytesIO()
    camera.capture_file(data, format='jpeg')
    logging.info("Image captured")
    camera.switch_mode(video_config)
    logging.info("Configuration changed: format: %s, resolution: %s",
        video_capture.encoder.format, video_capture.encoder.size)
    
    
    # Resume paused recording
    
    if video_capture_paused:
        video_capture.start()
    
    stop_camera()

    # Change the stream position to start for Minio to get correct bytes

    data.seek(0)
    
    # Upload to Minio

    result = client().put_object(
        bucket, "capture.jpg", data, len(data.getvalue()),
        content_type="image/jpg")
    
    logging.info("created %s object; etag: %s",
        result.object_name, result.etag)   

class VideoCapture():
    data = io.BytesIO()
    encoder = H264Encoder()    
    
    def start(self):
        camera.start_encoder(
        encoder=self.encoder, 
        output = FileOutput(self.data), 
        quality=Quality.MEDIUM, name="main")
        start_camera()
        logging.info("Recording started/resumed.")
    
    def stop(self):
        camera.stop_encoder(encoders=[self.encoder])
        stop_camera()
        logging.info("Recording stopped.")
        
    
    def upload(self, file_name):
    
        self.data.seek(0)
        logging.info("Uploading video...")
        result = client().put_object(
        bucket, file_name + ".h264", self.data, len(self.data.getvalue()),
        content_type="video/h264")
        self.data.seek(0)
        self.data.truncate()
        logging.info("created %s object; etag %s",
            result.object_name, result.etag)
        
video_capture = VideoCapture()


class StreamingHandler(server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/video_start':
            with open('index.html', 'r') as f:
                html_string = f.read()
            content = html_string.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
            video_capture.start()
        elif self.path == '/video_stop':
            with open('index.html', 'r') as f:
                html_string = f.read()
            content = html_string.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
            video_capture.stop()
            video_capture.upload('test')
        elif self.path == '/still':
            with open('index.html', 'r') as f:
                html_string = f.read()
            content = html_string.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
            capture_still()
        elif self.path == '/index.html':
            with open('index.html', 'r') as f:
                html_string = f.read()
            content = html_string.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                if (len(stream_clients) < 1):
                    camera.start_encoder(
                        encoder=stream_encoder, 
                        quality=Quality.LOW, 
                        output=FileOutput(stream_output), 
                        name="lores")
                    start_camera()
                    logging.info("Streaming started.")
                    
                stream_clients.add(self.client_address)
                                
                while True:
                    with stream_output.condition:
                        stream_output.condition.wait()
                        frame = stream_output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                stream_clients.remove(self.client_address)
                if (len(stream_clients) < 1):
                    camera.stop_encoder()
                    stop_camera()
                logging.info(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    
    
    allow_reuse_address = True
    daemon_threads = True


def run_server():  
        
       
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
        
    finally:    
        camera.stop_encoder()
        camera.stop()
        

if __name__ == "__main__":
    run_server()
