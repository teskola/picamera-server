import logging
import socketserver
import json
import cgi
from threading import Thread
from http import server
from pprint import pformat
from picamera2.encoders import Quality

from minio_client import MinioClient
from camera import Camera, RunningError, RunningError, Resolutions

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

camera = Camera()
minio = MinioClient()
stream_clients = set()

class CameraHandler(server.BaseHTTPRequestHandler): 

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:5173')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS, POST')
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        
   

    def send(self, code : int, response : dict = {}):
        if int(code / 100) == 2:
            self.send_response(code)
        else:
            self.send_error(code)
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:5173')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS, POST')
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode(encoding='utf_8'))

    def field_check_failed(self, list : list, payload : dict):
        for item in list:
            if item not in payload:
                self.send(400, {"error": f"Missing field: {item}"})
                return True
        return False
    # https://gist.github.com/nitaku/10d0662536f37a087e1b
    
    def do_POST(self):

        if self.path != '/api':
            self.send(404)
            return

        ctype, pdict = cgi.parse_header(self.headers.get('Content-Type'))
        
        # refuse to receive non-json content
        if ctype != 'application/json':
            logging.warning(f"Refused non-json content: {ctype}")
            self.send(400, {"error": "Refused non-json content"})
            return
            
        # read the message and convert it into a python dictionary
        length = int(self.headers.get('content-length'))
        fields = json.loads(self.rfile.read(length))       
        
        if self.field_check_failed(["action"], fields):
            return
        
        elif fields["action"] == "video_start":
            if self.field_check_failed(["resolution", "quality"], fields):                
                return            
            elif fields["resolution"] == "720p":
                resolution = Resolutions.P720
            elif fields["resolution"] == "1080p":
                resolution = Resolutions.P1080
            else:
                self.send(400, {"error": "Invalid resolution."})
                return            
            if fields["quality"] == 1:
                quality = Quality.VERY_LOW
            elif fields["quality"] == 2:
                quality = Quality.LOW
            elif fields["quality"] == 3:
                quality = Quality.MEDIUM
            elif fields["quality"] == 4:
                quality = Quality.HIGH
            elif fields["quality"] == 5:
                quality = Quality.VERY_HIGH
            else:
                self.send(400, {"error": "Invalid quality."})
                return
            camera.lock.acquire()
            cam_response = camera.recording_start(resolution=resolution, quality=quality)
            camera.lock.release()
            if "error" in cam_response:
                if cam_response["error"] is RunningError:
                    code = 409
                    cam_response["error"] = "Already recording."
                else:
                    code = 500
                    cam_response["error"] = "Something went wrong!"
            else:
                code = 200
            self.send(code, cam_response)

        elif fields["action"] == "video_stop":
            camera.lock.acquire()
            cam_response = camera.recording_stop()
            camera.lock.release()
            response = {}
            code = 200
            if "error" in cam_response:
                if cam_response["error"] is RunningError:
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
            self.send(code, response)
            #if code == 200:
            #    minio.upload_video(cam_response["data"], 'video')
                

        elif fields["action"] == "still_start":
            if self.field_check_failed(["interval", "name", "limit", "full_res", "epoch", "delay"], fields):
                return
            logging.info(pformat(fields))
            camera.lock.acquire()
            cam_response = camera.still_start(interval=fields["interval"], 
                                              name=fields["name"], 
                                              limit=fields["limit"], 
                                              full_res=fields["full_res"], 
                                              upload=minio.upload_image,
                                              epoch=fields["epoch"],
                                              delay=fields["delay"])
            camera.lock.release()
            if "error" in cam_response:
                if cam_response["error"] is RunningError:
                    code = 409
                    cam_response["error"] = "Already recording."
                elif cam_response["error"] is (ValueError or AttributeError):
                    code = 409
                    cam_response["error"] = str(cam_response["error"])
                else:
                    code = 500
                    cam_response["error"] = "Something went wrong!"
            else:
                code = 200
            self.send(code, cam_response)
        
        elif fields["action"] == "still_stop":
            logging.info("still_stop")
            camera.lock.acquire()
            cam_response = camera.still_stop()
            camera.lock.release()
            if "error" in cam_response:
                if cam_response["error"] is RunningError:
                    code = 409
                    cam_response["error"] = "No stills scheduled."
                else:
                    code = 500
                    cam_response["error"] = "Something went wrong!"
            else:
                code = 200
            self.send(code, cam_response)
        else:
            self.send(400)

    
    def do_GET(self):   
        if self.path == '/status':
            camera.lock.acquire()
            cam_response = camera.get_status()
            camera.lock.release()
            if "error" in cam_response:
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
            self.send(404)


class CameraServer(socketserver.ThreadingMixIn, server.HTTPServer):
        
    allow_reuse_address = True
    daemon_threads = True


def run_server():          
       
    try:
        address = ('', 5000)
        server = CameraServer(address, CameraHandler)
        logging.info("Server start.")
        server.serve_forever()
            
    except KeyboardInterrupt:
        logging.info("Server shutdown.")
        
    finally:    
        camera.stop()        

if __name__ == "__main__":    
    run_server()
