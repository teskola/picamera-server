import logging
import io
from threading import Condition, Lock
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder, H264Encoder, Quality
from picamera2.outputs import FileOutput

STREAM_BITRATE = 2400000

class Resolutions:
    STREAM_16_9 = (426, 240)
    STREAM_4_3 = (320, 240)
    P480 = (640, 480)
    P720 = (1280, 720)
    P1080 = (1920, 1080)

class Video:
    def __init__(self) -> None:
        self.data = io.BytesIO()
        self.resolution = None
        self.quality = None

    def release(self) -> io.BytesIO:
        self.data.seek(0)
        result = self.data
        self.data.truncate()
        return result
   
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
                self.picam2.create_video_configuration(
                    main={"size": Resolutions.STREAM_4_3}
                ),
            'still':
                self.picam2.create_still_configuration()
            }

    def __init__(self) -> None:
        self.picam2 = Picamera2()
        self.configurations = self._create_configurations()
        self.encoders = {'stream': MJPEGEncoder(bitrate=STREAM_BITRATE), 'record': H264Encoder()}
        self.streaming_output = StreamingOutput()
        logging.info("Configure to still.")
        self.picam2.configure(self.configurations["still"])
        self.video = Video()
        self.lock = Lock()

    def _encoders_running(self) -> bool:
        return len(self.picam2.encoders) > 0
    
    def preview_running(self) -> bool:
        return self.encoders["stream"] in self.picam2.encoders


    def _start_record_encoder(self):
        self.picam2.start_encoder(
            encoder=self.encoders['record'],
            output=FileOutput(self.video.data),
            quality=self.video.quality,
            name="main"
        )

    def _start_stream_encoder(self, lores=False):
        self.picam2.start_encoder(
            encoder=self.encoders["stream"],
            output=FileOutput(self.streaming_output),
            name="lores" if lores else "main"
        )

    def stop(self):
        self.picam2.stop_encoder()
        self.picam2.stop()

    def recording_start(self, resolution, quality) -> bool:
        if self.encoders["record"] in self.picam2.encoders:
            logging.warn("Recording already running.")
            return False
        stream_paused = False
        if self.encoders["stream"] in self.picam2.encoders:
            self.picam2.stop_encoder()
            logging.info("Stream paused.")
            stream_paused = True
            self.picam2.stop()

        logging.info("Configure to %s", resolution)
        self.picam2.configure(self.configurations[resolution])
        self.video.resolution = resolution
        self.video.quality = quality
        self._start_record_encoder()
        logging.info("Recording started.")
        if stream_paused:
            self._start_stream_encoder(lores=True)
            logging.info("Stream resumed.")
        self.picam2.start()

    def _recording_resume(self):
        logging.info("Configure to %s", self.video.resolution)
        self.picam2.configure(self.configurations[self.video.resolution])
        self._start_record_encoder()
        logging.info("Recording resumed.")

    def recording_stop(self) -> bool:
        if not self.encoders["record"] in self.picam2.encoders:
            logging.warn("Recording not running.")
            return False
        stream_running = False
        if self.encoders['stream'] in self.picam2.encoders:
            stream_running = True
        self.picam2.stop_encoder()
        self.picam2.stop()

        logging.info("Recording stopped.")
        if stream_running:
            logging.info("Stream paused.")

        if not stream_running:
            logging.info("Configure to still.")
            self.picam2.configure(self.configurations['still'])
        else:
            logging.info("Configure to preview.")
            self.picam2.configure(self.configurations['preview'])
            self._start_stream_encoder()
            logging.info("Streaming resumed.")
            self.picam2.start()
        return True

    def recording_data(self) -> io.BytesIO:
        return self.video.release()    

    def capture_still(self):

        # If recording, pause recording and configure for still image.

        paused_encoders = self.picam2.encoders.copy()

        if self._encoders_running():
            self.picam2.stop_encoder()
            logging.info("Recording/streaming paused.")
            logging.info("Configure to still.")
            self.picam2.switch_mode(self.configurations['still'])
        else:
            self.picam2.start()

        data = io.BytesIO()
        self.picam2.capture_file(data, format='jpeg')
        self.picam2.stop()

        if len(paused_encoders) > 0:
            if self.encoders['record'] in paused_encoders:
                self._recording_resume()
            if self.encoders['stream'] in paused_encoders:
                self._preview_resume()
            self.picam2.start()

        data.seek(0)
        return data

    def preview_start(self) -> bool:
        if self.encoders["stream"] in self.picam2.encoders:
            logging.warn("Stream already running.")
            return False        
        if not self._encoders_running():
            logging.info("Configure to stream.")
            self.picam2.configure(self.configurations['preview'])
            self._start_stream_encoder()
            logging.info("Streaming started.")
            self.picam2.start()
        else:
            self._start_stream_encoder(lores=True)
            logging.info("Streaming started.")
        return True

    def _preview_resume(self):
        if not self._encoders_running():
            logging.info("Configure to stream.")
            self.picam2.configure(self.configurations['preview'])

        self._start_stream_encoder()
        logging.info("Streaming resumed.")


    def preview_stop(self) -> bool:
        if not self.encoders["stream"] in self.picam2.encoders:
            logging.warn("Stream not running")
            return False

        self.picam2.stop_encoder(encoders=[self.encoders["stream"]])
        logging.info("Streaming stopped.")
        if not self._encoders_running():
            self.picam2.stop()
            logging.info("Configure to still.")
            self.picam2.configure(self.configurations['still'])
        return True
