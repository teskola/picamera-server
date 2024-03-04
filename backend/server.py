import logging
import socketserver
import json
import sched
import time
from http import server
from threading import Lock
from picamera2.encoders import Quality

from minio_client import MinioClient
from camera import Camera

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

scheduler = sched.scheduler(time.time, time.sleep)
capture_timer = None
count = 0
limit = 0
lock = Lock()
camera = Camera()
minio = MinioClient()
stream_clients = set()

def capture_and_upload(name):
    global count
    if limit > 0 and count >= limit:
        stop_capture_timer()

    else:
        camera.lock.acquire()
        data = camera.capture_still()
        camera.lock.release()
        count += 1
        return minio.upload_image(data, name)       

def set_capture_timer(interval : float, name : str, _limit : int = 0):
    global limit, capture_timer
    limit = _limit
    if scheduler.empty():
        capture_timer = scheduler.enter(interval, 1, capture_and_upload, argument=(name,))
        scheduler.run()

def stop_capture_timer():
    global capture_timer, count, limit
    scheduler.cancel(capture_timer)
    capture_timer = None
    count = 0
    limit = 0

class StreamingHandler(server.BaseHTTPRequestHandler):
    
    def do_GET(self):        
        if self.path == '/video_start':            
            self.send_response(200)
            self.end_headers()
            camera.lock.acquire()
            camera.recording_start(resolution='720p', quality=Quality.MEDIUM)
            camera.lock.release()
        elif self.path == '/video_stop':                       
            camera.lock.acquire()
            stopped = camera.recording_stop()
            camera.lock.release()
            if stopped:
                self.send_response(200)
                minio.upload_video(camera.recording_data(), 'video') 
            else:
                self.send_response(409)
            self.end_headers()           
        elif self.path == '/still':
            camera.lock.acquire()
            data = camera.capture_still()
            camera.lock.release()
            response = minio.upload_image(data, 'capture')
            json_string = json.dumps(response)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json_string.encode(encoding='utf_8'))
        elif self.path == '/timelapse':
            camera.lock.acquire()
            data = camera.capture_timelapse(0.120,100)
            camera.lock.release()
            response = []
            i = 0
            while i < len(data):
                data[i].seek(0)
                response.append(minio.upload_image(data[i], f'timelapse/capture{i}'))
                i = i + 1                
            json_string = json.dumps(response)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json_string.encode(encoding='utf_8'))
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
    set_capture_timer(5.0, "testi", 5)
    run_server()
