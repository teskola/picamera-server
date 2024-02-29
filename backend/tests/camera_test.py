import unittest
import threading
import time
from camera import Camera

class FrameRateTests(unittest.TestCase):

    framecount = 0

    def _increase_frame_count(self, request):
        global framecount
        framecount += 1

    def streamFrameRate(self):
        self.camera = Camera()
        self.camera.picam2.pre_callback = self._increase_frame_count

        t1 = threading.Thread(target=self.camera.preview_start)
        time.sleep(10)
        self.camera.preview_stop()
        self.assertTrue(framecount > 290)

    

if __name__ == '__main__':
    unittest.main()