#!/usr/bin/python3

# This is the same as mjpeg_server.py, but uses the h/w MJPEG encoder.

import io
import logging
import socketserver

from http import server
from threading import Condition

from client import client
from camera import instance as camera
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    
    def capture_still(self):
        bucket = "raspberry"

        # Configure for high-quality still picture, take picture

        camera_config = camera.create_still_configuration()
        camera.switch_mode(camera_config)
        data = io.BytesIO()
        camera.capture_file(data, format='jpeg')
        camera.switch_mode(camera.create_video_configuration(main={"size": (640, 480)}))

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
            self.capture_still()
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
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
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


camera.configure(camera.create_video_configuration(main={"size": (640, 480)}))
output = StreamingOutput()
camera.start_recording(MJPEGEncoder(), FileOutput(output))

try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    camera.stop_recording()
