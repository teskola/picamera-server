#!/usr/bin/python3

# This is the same as mjpeg_server.py, but uses the h/w MJPEG encoder.

import io
import logging
import socketserver

from http import server
from threading import Condition

from client import client
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder, H264Encoder
from picamera2.outputs import FileOutput

camera_running = False
stream_counter = 0
camera = Picamera2()

# Main configuration for captured videos, lores configuration for stream

video_config = camera.create_video_configuration(main={"size": (1280, 720)}, lores={"size": (160, 120)})
still_config = camera.create_still_configuration()
bucket = "raspberry"

camera.configure(video_config)
    

def start_camera():
    global camera_running
    if not camera_running:
        camera.start()
        camera_running = True

def stop_camera():
    global camera_running
    if not (video_capture.recording or video_stream.streaming):
        camera.stop()
        camera_running = False

def capture_still():
    
        start_camera()
    
        # Configure for high-quality still picture, take picture and switch back to streaming config
        
        camera.switch_mode(still_config)
        data = io.BytesIO()
        camera.capture_file(data, format='jpeg')
        camera.switch_mode(video_config)
        
        stop_camera()

        # Change the stream position to start for Minio to get correct bytes

        data.seek(0)
        
        # Upload to Minio

        result = client().put_object(
            bucket, "capture.jpg", data, len(data.getvalue()),
            content_type="image/jpg")


        print(
            "created {0} object; etag: {1}".format(
                result.object_name, result.etag,
            ))


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()




class VideoCapture():
    recording = False
    data = io.BytesIO()
    encoder = H264Encoder()
    encoder.size = video_config["main"]["size"]
    encoder.format = video_config["main"]["format"]
    encoder.output = FileOutput(data)
    
    def start(self):
        self.recording = True        
        camera.start_encoder(self.encoder)
        start_camera()
    
    def stop(self):
        self.recording = False
        self.encoder.stop()
        stop_camera()
        
    
    def upload(self, file_name):
    
        self.data.seek(0)
        result = client().put_object(
        bucket, file_name + ".h264", self.data, len(self.data.getvalue()),
        content_type="video/h264")
        self.data.seek(0)
        self.data.truncate()
        print(
            "created {0} object; etag: {1}".format(
                result.object_name, result.etag,
            ))



class VideoStream():
    
    def __init__(self):
        self.streaming = False    
        self.output = StreamingOutput()
        self.encoder = MJPEGEncoder()
        self.encoder.framerate = 30
        self.encoder.size = video_config["lores"]["size"]
        self.encoder.format = video_config["lores"]["format"]
        self.encoder.bitrate = 5000000    
        self.encoder.output = FileOutput(self.output) 
        

    def start(self):
        self.streaming = True
        camera.start_encoder(self.encoder) 
        start_camera()       
    
    def stop(self):
        self.streaming = False
        self.encoder.stop()
        stop_camera()
            

video_capture = VideoCapture()
video_stream = VideoStream()


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
                #global stream_counter
                #if not video_stream.streaming:
                #    video_stream.start()
                #stream_counter+=1
                while True:
                    with video_stream.output.condition:
                        video_stream.output.condition.wait()
                        frame = video_stream.output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                #stream_counter-=1
                #if (stream_counter < 1):
                #    stop_camera()
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    
    
    allow_reuse_address = True
    daemon_threads = True


def run_server():  
    
    camera.start_encoder(encoder=video_stream.encoder, output=video_stream.encoder.output, name="lores")
    camera.start()
       
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
        
    finally:    
        if video_stream.streaming:
            video_stream.stop()
        if video_capture.recording:
            video_capture.stop()
        camera.stop()
        

if __name__ == "__main__":
    run_server()
