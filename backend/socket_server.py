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

class CameraHandler(socketserver.StreamRequestHandler):
 
    def handle(self):
        self.data = self.request.recv(1024).strip().decode('utf-8').split()
        response = ''
        if (self.data[0] == 'status'):
            camera.lock.acquire()
            response = camera.status()
            camera.lock.release()
        elif (self.data[0] == 'still_start'):
            logging.info('still_start')
        elif (self.data[0] == 'still_stop'):
            logging.info('still_stop')
        elif (self.data[0] == 'video_start'):
            logging.info('video_start')
        elif (self.data[0] == 'video_stop'):
            logging.info('video_stop')
        else:
            logging.error(f'unkown command: {self.data}')
            
        
        self.request.sendall(json.dumps(response).encode(encoding='utf_8'))
            
controlServer = socketserver.TCPServer(("", 9090), CameraHandler)
controlServer.serve_forever()