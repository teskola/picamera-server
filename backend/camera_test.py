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

    def test_framerate(self):
        self.camera = Camera()
        self.camera.picam2.pre_callback = self._increase_frame_count

        t1 = threading.Thread(target=self.camera.preview_start)
        t1.start()
        time.sleep(10)
        self.camera.preview_stop()
        t1.join()
        self.assertTrue(framecount > 290)

    

if __name__ == '__main__':
    unittest.main()