import socketserver
import logging
import json
import traceback
from pprint import pformat
from minio_client import MinioClient
from camera import Camera, Resolutions
from picamera2.encoders import Quality


logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

camera = Camera()
minio = MinioClient()

class CameraServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

class CameraHandler(socketserver.StreamRequestHandler):   

    def delete(self, id) -> dict:
        camera.lock.acquire()
        response = camera.delete_video(id)
        camera.lock.release()
        return response
    
    def resolution(self, res : str) -> Resolutions:
        if (res == '720p'):
            return Resolutions.P720
        if (res == '1080p'):
            return Resolutions.P1080
        raise ValueError('Invalid resolution')
    
    def quality(self, q : int) -> Quality:
        if (q == 1):
            return Quality.VERY_LOW
        if (q == 2):
            return Quality.LOW
        if (q == 3):
            return Quality.MEDIUM
        if (q == 4):
            return Quality.HIGH
        if (q == 5):
            return Quality.VERY_HIGH
        raise ValueError('Invalid quality')
        
    def action(self, data) -> dict:
        if (data["action"] == 'status'):
            camera.lock.acquire()
            response = camera.status()
            camera.lock.release()
            return response
        if (data["action"] == 'still_start'):            
            camera.lock.acquire()
            response = camera.still_start(interval=data["interval"], 
                                              name=data["name"], 
                                              limit=data["limit"], 
                                              full_res=data["full_res"],  
                                              epoch = data["epoch"],                                          
                                              delay = data["delay"],
                                              upload=minio.upload_image,
                                              )
            camera.lock.release()
            return response
        if (data["action"] == 'still_stop'):
            camera.lock.acquire()
            response = camera.still_stop()
            camera.lock.release()
            return response
        if (data["action"] == 'video_start'):
            camera.lock.acquire()
            response = camera.recording_start(resolution=self.resolution(data["resolution"]), 
                                              quality=self.quality(data["quality"]), 
                                              id=data["id"])
            camera.lock.release()
            return response
        if (data["action"] == 'video_stop'):
            camera.lock.acquire()
            response = camera.recording_stop()
            camera.lock.release()
            return response
        if (data["action"] == 'video_upload'):
            camera.lock.acquire()
            video = camera.find_video_by_id(data["id"])
            camera.lock.release()
            return minio.upload_video(data=video.data, 
                                      filename=data["name"], 
                                      on_complete=self.delete,
                                      args = data["id"])            
        if (data["action"] == 'video_delete'):
            return self.delete(data["id"])
        if (data["action"] == 'preview_start'):
            camera.lock.acquire()
            started = camera.preview_start()
            camera.lock.release()
            return {"started": started}
        if (data["action"] == 'preview_stop'):
            camera.lock.acquire()
            stopped = camera.preview_stop()
            camera.lock.release()       
            return {"stopped": stopped}
        if (data["action"] == 'preview_listen'):   
            while True:
                with camera.streaming_output.condition:
                    camera.streaming_output.condition.wait()
                    frame = camera.streaming_output.frame
                self.wfile.write(frame)

        else:
            logging.error(f'unkown command: {data["action"]}')
 
    def handle(self):
        try:
            req = self.request.recv(256)
            logging.info(f"Recieved {len(req)} bytes from {self.client_address}")
            data = json.loads(req)
            logging.info(f"{self.client_address[1]}:\n" + pformat(data))
            response = self.action(data)   
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as exc:   
            logging.error(f"{str(exc)}:\n-----ERROR START--------------\n {traceback.format_exc()} \n--------ERROR STOP------------\n")
            self.wfile.write(json.dumps({"error": {type(exc).__name__: str(exc)}}).encode())

def run_server():          
       
    try:
        address = ('127.0.0.1', 9090)
        server = CameraServer(address, CameraHandler)
        logging.info("Server start.")
        server.serve_forever()
            
    except KeyboardInterrupt:
        logging.info("Server shutdown.")
        
    finally:    
        camera.stop()        

if __name__ == "__main__":    
    run_server()