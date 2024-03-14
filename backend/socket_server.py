import socketserver
import logging
import json
from minio_client import MinioClient
from camera import Camera, AlreadyRunningError, NotRunningError, Resolutions

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

camera = Camera()
minio = MinioClient()

class CameraServer(socketserver.TCPServer):
    allow_reuse_address = True

class CameraHandler(socketserver.StreamRequestHandler):   
        
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
        elif (self.data["action"] == 'still_stop'):
            logging.info('still_stop')
        elif (self.data["action"] == 'video_start'):
            logging.info('video_start')
        elif (self.data["action"] == 'video_stop'):
            logging.info('video_stop')
        else:
            logging.error(f'unkown command: {self.data["action"]}')
 
    def handle(self):
        self.data = json.loads(self.request.recv(1024).decode('utf-8'))
        action = self.data["action"]
        print(f"Recieved request: {action} from {self.client_address[0]}")
        response = self.action()    
        self.request.sendall(json.dumps(response).encode(encoding='utf_8'))

def run_server():          
       
    try:
        address = ('', 9090)
        server = CameraServer(address, CameraHandler)
        logging.info("Server start.")
        server.serve_forever()
            
    except KeyboardInterrupt:
        logging.info("Server shutdown.")
        
    finally:    
        camera.stop()        

if __name__ == "__main__":    
    run_server()