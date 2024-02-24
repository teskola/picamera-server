import io
import logging
import socketserver
from http import server
from threading import Condition

from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder, H264Encoder, Quality
from picamera2.outputs import FileOutput

from backend.minio_client import MinioClient

logging.basicConfig(level=logging.INFO)

# https://github.com/raspberrypi/picamera2/blob/main/examples/mjpeg_server_2.py

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

# open camera

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

logging.info("Configure to still.")
camera.configure(still_config)

# minio

minio = MinioClient()

# encoders

stream_encoder = MJPEGEncoder()

def encoders_running():
    return len(camera.encoders) > 0


def start_camera():
    global camera_running
    if not camera_running:
        camera.start()
        camera_running = True

def stop_camera():
    global camera_running
    if not encoders_running():        
        camera.stop()
        logging.info("Configure to still.")
        camera.configure(still_config)
        camera_running = False

def capture_still():
        
    # Start camera, if not started yet
    
    start_camera()
    
    # If recording, pause recording. Configure for still image.
    
    video_capture_paused = False
            
    if encoders_running():        
        if video_capture.encoder in camera.encoders:
            camera.stop_encoder(encoders=[video_capture.encoder])
            video_capture_paused = True
            logging.info("Recording paused.")
        logging.info("Configure to still.")
        camera.switch_mode(still_config)
    
    data = io.BytesIO()
    camera.capture_file(data, format='jpeg')
    logging.info("Image captured")
        
    # Resume paused recording
    
    if encoders_running():
        logging.info("Configure to video.")
        camera.switch_mode(video_config)
        if video_capture_paused:
            video_capture.start()
    else:
        camera.stop()
        global camera_running
        camera_running = False   

    # Change the stream position to start for Minio to get correct bytes

    data.seek(0)
    
    # Upload to Minio

    minio.upload_image(data, "capture")      

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
        minio.upload_video(self.data, file_name)        
        self.data.seek(0)
        self.data.truncate()
                
video_capture = VideoCapture()


class StreamingHandler(server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/stream.mjpg')
            self.end_headers()
        elif self.path == '/video_start':            
            self.send_response(200)
            self.end_headers()
            video_capture.start()
        elif self.path == '/video_stop':            
            self.send_response(200)            
            self.end_headers()
            video_capture.stop()
            video_capture.upload('test')
        elif self.path == '/still':  
            capture_still()          
            self.send_response(200)            
            self.end_headers()        
        elif self.path == '/stream.mjpg':
            
            if not encoders_running():
                logging.info("Configure to video.")
                camera.configure(video_config)
                camera.start_encoder(
                    encoder=stream_encoder, 
                    quality=Quality.LOW, 
                    output=FileOutput(stream_output), 
                    name="lores")
                start_camera()
                logging.info("Stream started.")

            stream_clients.add(self.client_address)            
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            
            try:               
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
                logging.info(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
                if (len(stream_clients) < 1):
                    camera.stop_encoder(encoders=[stream_encoder])
                    logging.info("Stream stopped.")                    
                    stop_camera()
                
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
