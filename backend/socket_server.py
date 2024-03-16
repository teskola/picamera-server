import socketserver
import logging
import json
from minio_client import MinioClient
from camera import Camera, Resolutions
from picamera2.encoders import Quality


logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

camera = Camera()
minio = MinioClient()

class CameraServer(socketserver.TCPServer):
    allow_reuse_address = True

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
        
    def action(self) -> dict:
        if (self.data["action"] == 'status'):
            camera.lock.acquire()
            response = camera.status()
            camera.lock.release()
            return response
        if (self.data["action"] == 'still_start'):            
            camera.lock.acquire()
            response = camera.still_start(interval=self.data["interval"], 
                                              name=self.data["name"], 
                                              limit=self.data["limit"], 
                                              full_res=self.data["full_res"],  
                                              epoch = self.data["epoch"],                                          
                                              delay = self.data["delay"],
                                              upload=minio.upload_image,
                                              )
            camera.lock.release()
            return response
        if (self.data["action"] == 'still_stop'):
            camera.lock.acquire()
            response = camera.still_stop()
            camera.lock.release()
            return response
        if (self.data["action"] == 'video_start'):
            camera.lock.acquire()
            response = camera.recording_start(resolution=self.resolution(self.data["resolution"]), 
                                              quality=self.quality(self.data["quality"]), 
                                              id=self.data["id"])
            camera.lock.release()
            return response
        if (self.data["action"] == 'video_stop'):
            camera.lock.acquire()
            response = camera.recording_stop(id=self.data["id"])
            camera.lock.release()
            return response
        if (self.data["action"] == 'video_upload'):
            camera.lock.acquire()
            video = camera.find_video_by_id(self.data["id"])
            camera.lock.release()
            return minio.upload_video(data=video.data, 
                                      filename=self.data["name"], 
                                      cb=self.delete(self.data["id"]))            
        if (self.data["action"] == 'video_delete'):
            return self.delete(self.data["id"])
        else:
            logging.error(f'unkown command: {self.data["action"]}')
 
    def handle(self):
        self.data = json.loads(self.rfile.readline().strip())
        action = self.data["action"]
        print(f"Recieved request: {action} from {self.client_address[0]}")
        response = self.action()    
        self.wfile.write(json.dumps(response).encode(encoding='utf-8'))

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