import logging
import io
from threading import Condition
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder, H264Encoder, Quality
from picamera2.outputs import FileOutput

class Resolutions:
    STREAM_4_3 = (320,240)
    STREAM_16_9 = (426,240)
    P480 = (640, 480)
    P720 = (1280, 720)
    P1080 = (1920, 1080)

class Recording:
    def __init__(self, resolution, quality) -> None:
        self.data = io.BytesIO()
        self.resolution = resolution
        self.quality = quality

# https://github.com/raspberrypi/picamera2/blob/main/examples/mjpeg_server_2.py

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


class Camera:
    def StreamEncoder(self):
        encoder = MJPEGEncoder()
        encoder.framerate = 30
        return encoder
    
    def _create_configurations(self):
        return {
            '480p': 
                self.picam2.create_video_configuration(
                    main={"size": Resolutions.P480}, 
                    lores={"size": Resolutions.STREAM_4_3}
                ),
            '720p':
                self.picam2.create_video_configuration(
                    main={"size": Resolutions.P720},
                    lores={"size": Resolutions.STREAM_16_9}
                ),
            '1080p':
                self.picam2.create_video_configuration(
                    main={"size": Resolutions.P1080},
                    lores={"size": Resolutions.STREAM_16_9}
                ),
            'preview':
                self.picam2.create_still_configuration(
                    lores={"size": Resolutions.STREAM_4_3},
                    buffer_count=4
                ),
            'still':
                self.picam2.create_still_configuration()
            }

    def __init__(self) -> None:
        self.picam2 = Picamera2()
        self.running = False
        self.configurations = self._create_configurations()
        self.encoders = {'stream': self.StreamEncoder(), 'record': H264Encoder()}
        self.streaming_output = StreamingOutput()
        logging.info("Configure to still.")
        self.picam2.configure(self.configurations["still"])
        self.recording = None        
    
    def _encoders_running(self):
        return len(self.picam2.encoders) > 0
    
    def _start(self):
        if not (self.running):
            self.picam2.start()
            self.running = True
    
    def close(self):
        self.picam2.stop_encoder()
        self.picam2.stop()
    
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
        self._start()
        logging.info("Recording started.")
    
    def recording_resume(self):
        logging.info("Configure to %s", self.recording.resolution)
        self.picam2.switch_mode(self.configurations[self.recording.resolution])
        self.picam2.start_encoder(
            encoder=self.encoders('record'),
            output=FileOutput(self.recording.data),
            quality=self.recording.quality,
            name="main"
        )
        logging.info("Recording resumed.")
    
    # Stops recording and returns recorded data.

    def recording_stop(self):
        self.picam2.stop_encoder(encoders=[self.encoders['record']])
        logging.info("Recording stopped.")
        if not self._encoders_running():
            self.picam2.stop()
            logging.info("Configure to still.")
            self.picam2.configure(self.configurations['still'])
            self.running = False
        else:
            logging.info("Configure to preview.")
            self.picam2.configure(self.configurations['preview'])
        data = self.recording.data
        self.recording = None
        data.seek(0)
        return data
    
    def capture_still(self):
        self._start()       
    
        # If recording, pause recording and configure for still image.
        
        if self.encoders['record'] in self.picam2.encoders:
            self.picam2.stop_encoder(encoders=[self.encoders['record']])
            logging.info("Recording paused.")
            logging.info("Configure to still.")
            self.picam2.switch_mode(self.configurations['still'])       
        
        data = io.BytesIO()
        self.picam2.capture_file(data, format='jpeg')
        
        if self._encoders_running():
            if self.encoders['record'] in self.picam2.encoders:
                self.recording_resume()          
        else:
            self.picam2.stop()
            self.running = False
        
        data.seek(0)
        return data
    
    def preview_start(self):
        if not self._encoders_running():
            logging.info("Configure to stream.")
            self.picam2.configure(self.configurations['preview'])
        
        self.picam2.start_encoder(
            encoder=self.encoders["stream"],
            quality=Quality.MEDIUM,
            output=FileOutput(self.streaming_output),
            name="lores"
        )
        self._start()
        logging.info("Streaming started.")

    def preview_stop(self):
        self.picam2.stop_encoder(encoders=[self.encoders["stream"]])
        logging.info("Streaming stopped.")
        if not self._encoders_running():
            self.picam2.stop()
            logging.info("Configure to still.")
            self.picam2.configure(self.configurations['still'])
            self.running = False
        
        