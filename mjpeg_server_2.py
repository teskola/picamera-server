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

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

camera = Picamera2()

# Main configuration for captured videos, lores configuration for stream

video_config = camera.create_video_configuration(main={"size": (1280, 720)}, lores={"size": (640, 480)})
still_config = camera.create_still_configuration()
stream_output = StreamingOutput()
video_encoder = H264Encoder()


class StreamingHandler(server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
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
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    
    
    allow_reuse_address = True
    daemon_threads = True


# def start_recording():
    

def capture_still():
        bucket = "raspberry"

        # Configure for high-quality still picture, take picture and switch back to streaming config

        camera.switch_mode(still_config)
        data = io.BytesIO()
        camera.capture_file(data, format='jpeg')
        camera.switch_mode(video_config)

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

def main():  
    
    camera.configure(video_config)
    mjpeg_encoder = MJPEGEncoder()
    mjpeg_encoder.framerate = 30
    mjpeg_encoder.size = video_config["lores"]["size"]
    mjpeg_encoder.format = video_config["lores"]["format"]
    mjpeg_encoder.bitrate = 5000000    
    mjpeg_encoder.output = FileOutput(stream_output)
    video_encoder.output = FileOutput('test.h264')
    camera.start_encoder(mjpeg_encoder)
    camera.start_encoder(video_encoder)
    camera.start() 
    

    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
        
    finally:    
        mjpeg_encoder.stop()
        video_encoder.stop()
        camera.stop()
        

if __name__ == "__main__":
    main()
