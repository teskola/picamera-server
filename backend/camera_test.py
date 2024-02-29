import unittest
import threading
import time
from camera import Camera

class FrameRateTests(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        self.framecount = 0
        super().__init__(methodName)    

    def _increase_frame_count(self, request):        
        self.framecount += 1

    def test_framerate_30(self):
        camera = Camera()
        camera.picam2.pre_callback = self._increase_frame_count

        t1 = threading.Thread(target=camera.preview_start)
        t1.start()
        time.sleep(10)
        camera.preview_stop()
        camera.close()
        t1.join()
        print(f"{self.framecount} frames in 10 seconds")
        self.assertTrue(self.framecount > 275)
        self.assertTrue(self.framecount < 300)
        self.framecount = 0
        
    
    def test_framerate_50(self):
        camera = Camera()
        camera.picam2.pre_callback = self._increase_frame_count
        camera.capture_timelapse(interval=20)        
        print(f"{self.framecount} frames in 10 seconds")
        self.assertTrue(self.framecount > 400)
        self.assertTrue(self.framecount < 500)
        self.framecount = 0

    

if __name__ == '__main__':
    unittest.main()