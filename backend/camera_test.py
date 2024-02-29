import unittest
from threading import Thread
from time import sleep
import io
from camera import Camera
from picamera2 import Picamera2
from libcamera import controls

class FrameRateTests(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        self.framecount = 0
        self.captured_images = 0
        super().__init__(methodName)
        self.camera=None

    def _increase_frame_count(self, request):        
        self.framecount += 1   
    
    def _capture_jpg(self):
        #self.camera.capture_still()
        data = io.BytesIO()
        self.camera.picam2.capture_file(data, format='jpeg')
        self.captured_images += 1
    
    def test_framerate_30(self):
        self.camera = Camera()
        self.camera.picam2.pre_callback = self._increase_frame_count        
        self.camera.picam2.configure(self.camera.configurations["still"]["fast"])
        sleep(10)
        self.camera.picam2.stop()
        self.camera.picam2.close()
        self.camera = None
        print(f"{self.framecount} frames in 10 seconds")
        self.assertGreater(self.framecount, 475)
        self.assertLess(self.framecount, 500)
        
        
    def test_fast_capture(self):        
        self.camera = Camera()
        result = self.camera.capture_timelapse(3, 5)
        self.assertEqual(len(result), self.captured_images)
        for image in result:
            self.assertGreater(len(image.getvalue()), 0) 

        self.camera.picam2.close()
    
if __name__ == '__main__':
    unittest.main()