import unittest
import threading
import time
import io
import sched
from camera import Camera
from picamera2 import Picamera2
from libcamera import controls
from apscheduler.schedulers import BackgroundScheduler

class FrameRateTests(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        self.framecount = 0
        self.captured_images = 0
        super().__init__(methodName)    

    def _increase_frame_count(self, request):        
        self.framecount += 1   
    
    def _capture_jpg(self):
        data = io.BytesIO()
        self.picam2.capture_file(data, format='jpeg')
        self.captured_images += 1
        
    def test_fast_capture(self):
        picam2 = Picamera2()
        picam2.configure(picam2.create_still_configuration())
        picam2.start()
        sched = BackgroundScheduler()
        sched.start()
        sched.add_interval_job(self._capture_jpg, seconds = 1)  
        time.sleep(10)      
        sched.shutdown()        
        picam2.close()
        self.assertEqual(self.framecount, 10)
        self.captured_images = 0
        picam2.close()
    
    def test_framerate_30(self):
        camera = Camera()
        camera.picam2.pre_callback = self._increase_frame_count
        
        t1 = threading.Thread(target=camera.preview_start)
        t1.start()
        time.sleep(10)
        camera.preview_stop()
        camera.picam2.close()
        t1.join()
        print(f"{self.framecount} frames in 10 seconds")
        self.assertGreater(self.framecount, 275)
        self.assertLess(self.framecount, 300)
        self.framecount = 0

    

if __name__ == '__main__':
    unittest.main()