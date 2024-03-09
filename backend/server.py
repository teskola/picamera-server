import logging
import socketserver
import json
from http import server
from picamera2.encoders import Quality

from minio_client import MinioClient
from camera import Camera, AlreadyRunningError, NotRunningError

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

camera = Camera()
minio = MinioClient()
stream_clients = set()

class StreamingHandler(server.BaseHTTPRequestHandler):    

    def send(self, code : int, response : dict):
        if int(code / 100) == 2:
            self.send_response(code)
        else:
            self.send_error(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode(encoding='utf_8'))
    
    def do_GET(self):   
        if self.path == '/status':
            camera.lock.acquire()
            cam_response = camera.status()
            camera.lock.release()
            if "error" in cam_response:
                code = 500
                cam_response["error"] = "Something went wrong!"    
            else:
                code = 200       
            self.send(code, cam_response)

        elif self.path == '/video_start':            
            camera.lock.acquire()
            cam_response = camera.recording_start(resolution='720p', quality=Quality.MEDIUM)
            camera.lock.release()
            if "error" in cam_response:
                if cam_response["error"] is AlreadyRunningError:
                    code = 409
                    cam_response["error"] = "Already recording."
                else:
                    code = 500
                    cam_response["error"] = "Something went wrong!"
            else:
                code = 200
            self.send(code, cam_response)

        elif self.path == '/video_stop':                       
            camera.lock.acquire()
            cam_response = camera.recording_stop()
            camera.lock.release()
            response = {}
            code = 200
            if "error" in cam_response:
                if cam_response["error"] is NotRunningError:
                    code = 409
                    response["error"] = "Not recording."
                else:
                    code = 500
                    response["error"] = "Something went wrong!"
            if "status" in cam_response:
                response['status'] = cam_response['status']

            if "data" not in cam_response or cam_response['data'] is None:                
                code = 500
                response["error"] = "Something went wrong!"
            if code == 200:
                minio.upload_video(cam_response["data"], 'video') 
            self.send(code, response)   

        elif self.path == '/still_start':
            camera.lock.acquire()
            cam_response = camera.still_start(interval=2, name="testi", limit=0, full_res=False, upload=minio.upload_image)
            camera.lock.release()
            if "error" in cam_response:
                if cam_response["error"] is AlreadyRunningError:
                    code = 409
                    cam_response["error"] = "Already recording."
                else:
                    code = 500
                    cam_response["error"] = "Something went wrong!"
            else:
                code = 200
            self.send(code, cam_response)            

        elif self.path == '/still_stop':
            camera.lock.acquire()
            cam_response = camera.still_stop()
            camera.lock.release()
            if "error" in cam_response:
                if cam_response["error"] is NotRunningError:
                    code = 409
                    cam_response["error"] = "No stills scheduled."
                else:
                    code = 500
                    cam_response["error"] = "Something went wrong!"
            else:
                code = 200
            self.send(code, cam_response)


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
        logging.info("Server start.")
        server.serve_forever()
            
    except KeyboardInterrupt:
        logging.info("Server shutdown.")
        
    finally:    
        camera.stop()        

if __name__ == "__main__":    
    run_server()
