import logging
import io

from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder, H264Encoder, Quality
from picamera2.outputs import FileOutput

class Resolutions:
    P240 = (320,240)
    P480 = (640, 480)
    P720 = (1280, 720)
    P1080 = (1920, 1080)

class Recording:
    def __init__(self, resolution, quality) -> None:
        self.data = io.BytesIO()
        self.resolution = resolution
        self.quality = quality


class Camera:
    def _create_configurations(self):
        return {
            '480p': 
                self.picam2.create_video_configuration(
                    main={"size": Resolutions.P480}, 
                    lores={"size": Resolutions.P240}
                ),
            '720p':
                self.picam2.create_video_configuration(
                    main={"size": Resolutions.P720},
                    lores={"size": Resolutions.P240}
                ),
            '1080p':
                self.picam2.create_video_configuration(
                    main={"size": Resolutions.P1080},
                    lores={"size": Resolutions.P240}
                ),
            'still':
                self.picam2.create_still_configuration(
                    lores={"size": Resolutions.P240}
                )
            }

    def __init__(self) -> None:
        self.picam2 = Picamera2()
        self.running = False
        self.configurations = self._create_configurations()
        self.encoders = {'stream': MJPEGEncoder(), 'record': H264Encoder()}
        logging.info("Configure to still.")
        self.picam2.configure(self.configurations["still"])
        self.recording = None        
    
    def _encoders_running(self):
        return len(self.picam2.encoders) > 0
    
    def _start(self):
        if not (self.running):
            self.picam2.start()
            self.running = True
    
    def recording_start(self, resolution, quality):
        logging.info("Configure to %s", resolution)
        self.picam2.configure(self.configurations[resolution])
        self.recording = Recording(resolution=resolution, quality=quality)
        self.picam2.start_encoder(
            encoder=self.encoders('record'),
            output=FileOutput(self.recording.data),
            quality=self.recording.quality,
            name="main"
        )
        logging.info("Recording started.")
    
    def recording_resume(self):
        logging.info("Configure to %s", self.recording.resolution)
        self.picam2.configure(self.configurations[self.recording.resolution])
        self.picam2.start_encoder(
            encoder=self.encoders('record'),
            output=FileOutput(self.recording.data),
            quality=self.recording.quality,
            name="main"
        )
        logging.info("Recording resumed.")
    
    def recording_stop(self):
        self.picam2.stop_encoder(encoders=[self.encoders['record']])
        logging.info("Recording stopped.")

    
    def capture_still(self):
        self._start()       
    
        # If recording, pause recording. Configure for still image.    

        if self._encoders_running():
            if self.encoders['record'] in self.picam2.encoders:
                self.picam2.stop_encoder(encoders=[self.encoders['record']])
                logging.info("Recording paused.")
            logging.info("Configure to still.")
            self.picam2.switch_mode(self.configurations['still'])       
        
        data = io.BytesIO()
        self.picam2.capture_file(data, format='jpeg')
        
        # Resume paused recording

        if self._encoders_running():
            logging.info("Cofigure to video.")
            self.picam2.switch_mode(self.configurations['record'])
            if video_capture_paused:
                pass
        else:
            self.picam2.stop()
            self.running = False

        return data


