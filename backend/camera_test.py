import unittest
import threading
import time
from camera import Camera
from picamera2 import Picamera2
from libcamera import controls


class FrameRateTests(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        self.framecount = 0
        super().__init__(methodName)    

    def _increase_frame_count(self, request):        
        self.framecount += 1   
        
    def test_framerate_50(self):
        picam2 = Picamera2()
        picam2.pre_callback = self._increase_frame_count
        config = picam2.create_still_configuration(raw=picam2.sensor_modes[0])
        picam2.set_controls({"NoiseReductionMode": controls.draft.NoiseReductionModeEnum.Fast, 
                                  "AeEnable": False, 
                                  "AwbEnable": False, 
                                  "FrameDurationLimits": (1000000, 1000000)})
        picam2.configure(config)
        picam2.start()
        time.sleep(10)
        picam2.stop()
        print(f"{self.framecount} frames in 10 seconds")
        self.assertEqual(self.framecount, 10)
        self.framecount = 0
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