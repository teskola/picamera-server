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
        if (self.data[0] == 'status'):
            camera.lock.acquire()
            response = camera.status()
            camera.lock.release()
            return response
        if (self.data[0] == 'still_start'):
            if len(self.data) != 7:
                return {"error": f"Expected 7 arguments, got {len(self.data)}"}                
            camera.lock.acquire()
            response = camera.still_start(interval=int(self.data[1]), 
                                              name=self.data[2], 
                                              limit=int(self.data[3]), 
                                              full_res=self.data[4] == 'true',                                               
                                              delay=float(self.data[6]),
                                              upload=minio.upload_image,
                                              )
            camera.lock.release()
            return response
        elif (self.data[0] == 'still_stop'):
            logging.info('still_stop')
        elif (self.data[0] == 'video_start'):
            logging.info('video_start')
        elif (self.data[0] == 'video_stop'):
            logging.info('video_stop')
        else:
            logging.error(f'unkown command: {self.data}')
 
    def handle(self):
        self.data = self.request.recv(1024).strip().decode('utf-8').split()
        response = self.action()     
        self.request.sendall(json.dumps(response).encode(encoding='utf_8'))

controlServer = CameraServer(("", 9090), CameraHandler)
controlServer.serve_forever()