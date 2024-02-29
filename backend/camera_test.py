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
        
        
    def test_fast_capture(self):        
        self.camera = Camera()
        result = self.camera.capture_timelapse(5, 10)
        self.assertEqual(len(result), 10)
        for image in result:
            size = len(image.getvalue())
            print(f"Captured image size: {size}")
            self.assertGreater(len(image.getvalue()), 0)        
        self.camera.picam2.close()
    
 """    def test_framerate_30(self):
        self.camera = Camera()
        self.camera.picam2.pre_callback = self._increase_frame_count        
        t1 = Thread(target=self.camera.preview_start)
        t1.start()
        sleep(10)
        self.camera.preview_stop()
        self.camera.picam2.close()
        t1.join()
        print(f"{self.framecount} frames in 10 seconds")
        self.assertGreater(self.framecount, 275)
        self.assertLess(self.framecount, 300)
        self.framecount = 0
 """
    

if __name__ == '__main__':
    unittest.main()