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
        self.picam2 = None
        super().__init__(methodName)    

    def _increase_frame_count(self, request):        
        self.framecount += 1   
    
    def _capture_jpg(self):
        data = io.BytesIO()
        self.picam2.capture_file(data, format='jpeg')
        self.captured_images += 1
        
    def test_fast_capture(self):
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_still_configuration())
        self.picam2.start()
        for i in range(10):
            Thread(target=self._capture_jpg).start()
            sleep(1)                      
        self.picam2.close()
        self.assertEqual(self.framecount, 10)
        self.captured_images = 0
    
    def test_framerate_30(self):
        camera = Camera()
        camera.picam2.pre_callback = self._increase_frame_count
        
        t1 = Thread(target=camera.preview_start)
        t1.start()
        sleep(10)
        camera.preview_stop()
        camera.picam2.close()
        t1.join()
        print(f"{self.framecount} frames in 10 seconds")
        self.assertGreater(self.framecount, 275)
        self.assertLess(self.framecount, 300)
        self.framecount = 0

    

if __name__ == '__main__':
    unittest.main()