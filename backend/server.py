import logging
import socketserver
import json
import sched
import time
from http import server
from threading import Lock, Thread
from picamera2.encoders import Quality

from minio_client import MinioClient
from camera import Camera

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

camera = Camera()
minio = MinioClient()
stream_clients = set()

class StreamingHandler(server.BaseHTTPRequestHandler):
    
    def do_GET(self):   
        if self.path == '/status':
            camera.lock.acquire()
            response = camera.status()
            camera.lock.release()
            json_string = json.dumps(response)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json_string.encode(encoding='utf_8'))

        elif self.path == '/video_start':            
            self.send_response(200)
            self.end_headers()
            camera.lock.acquire()
            camera.recording_start(resolution='720p', quality=Quality.MEDIUM)
            camera.lock.release()

        elif self.path == '/video_stop':                       
            camera.lock.acquire()
            data = camera.recording_stop()
            camera.lock.release()
            if data is None:
                self.send_response(409)                
            else:
                self.send_response(200)
                minio.upload_video(data, 'video') 
            self.end_headers()           

        elif self.path == '/still_start':
            camera.lock.acquire()
            camera.still_start(interval=1, name="testi", limit=0, full_res=False, upload=minio.upload_image)
            camera.lock.release()
            self.send_response(200)
            self.end_headers()

        elif self.path == '/still_stop':
            camera.lock.acquire()
            camera.still_stop()
            camera.lock.release()
            self.send_response(200)
            self.end_headers()

        elif self.path == '/timelapse':
            camera.lock.acquire()
            camera.timelapse_test()
            camera.lock.release()
            self.send_response(200)
            self.end_headers()

        elif self.path == '/stream.mjpg':            
            if not camera.preview_running():
                camera.lock.acquire()
                camera.preview_start()
                camera.lock.release()
            stream_clients.add(self.client_address)
            logging.info("Added streaming client %s", self.client_address)

            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            
            try:               
                while True:
                    with camera.streaming_output.condition:
                        camera.streaming_output.condition.wait()
                        frame = camera.streaming_output.frame
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
                    camera.preview_stop()
                
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
        
    allow_reuse_address = True
    daemon_threads = True


def run_server():          
       
    try:
        address = ('', 5000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
        
    finally:    
        camera.stop()        

if __name__ == "__main__":    
    run_server()
