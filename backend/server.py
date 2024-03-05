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

scheduler = sched.scheduler(time.time, time.sleep)
task = None
count = 0
limit = 0
interval = 0
full_res = False
lock = Lock()
camera = Camera()
minio = MinioClient()
stream_clients = set()

def capture_and_upload(name : str):
    global count, task, full_res
    if limit == 0 or count < limit:
        task = scheduler.enter(interval, 1, capture_and_upload, argument=(name, ))
    keep_alive = interval < 20
    camera.lock.acquire()
    data = camera.capture_still(minio.upload_image, name, keep_alive=keep_alive, full_res=full_res) 
    count += 1 
    if limit != 0 and count == limit and keep_alive:
        camera.stop_timelapse()
    camera.lock.release()

def set_capture_timer(_interval : int, name : str, _limit : int = 0, _full_res : bool = False):
    global limit, interval, task, full_res
    limit = _limit
    interval = _interval
    full_res = _full_res
    if scheduler.empty():
        if interval < 20:
            camera.start(full_res=full_res)
        task = scheduler.enter(1, 1, capture_and_upload, argument=(name, ))
        scheduler.run()

def stop_capture_timer():
    global task, count, limit
    scheduler.cancel(task)
    task = None
    count = 0
    limit = 0  
    camera.stop_timelapse() 

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
            set_capture_timer(0.1, "testi", 0, False)
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
