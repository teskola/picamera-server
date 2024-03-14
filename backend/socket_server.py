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
        if (self.data == 'status'):
            camera.lock.acquire()
            response = camera.status()
            camera.lock.release()
            return response
        if (self.data[0] == 'still_start'):
            if len(self.data) != 7:
                return {"error": f"Expected 7 arguments, got {len(self.data)}"}  
            if (self.data[5] == 'null'):
                epoch = None
            else:
                epoch = int(self.data[5])
            if (self.data[6] == 'null'):
                delay = None
            else:
                delay = float(self.data[6])
            camera.lock.acquire()
            response = camera.still_start(interval=int(self.data[1]), 
                                              name=self.data[2], 
                                              limit=int(self.data[3]), 
                                              full_res=self.data[4] == 'true',  
                                              epoch = epoch,                                          
                                              delay = delay,
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
        self.data = self.request.recv(1024).decode('utf-8')
        print("Recieved one request from {}".format(self.client_address[0]))
        self.request.send(self.data)
        response = self.action()     
        self.request.sendall(json.dumps(response).encode(encoding='utf-8'))

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