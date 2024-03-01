import logging
import io
import time
import copy
from pprint import pformat
from threading import Condition, Lock
from libcamera import controls
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder, H264Encoder
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
        result = copy.deepcopy(self.data)
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
            'video': 
            {
                '240p':
                    self.picam2.create_video_configuration(
                        main={"size": Resolutions.STREAM_4_3},
                    ),
                '480p':
                    self.picam2.create_video_configuration(
                        main={"size": Resolutions.P480},
                        lores={"size": Resolutions.STREAM_4_3},
                    ),
                '720p':
                    self.picam2.create_video_configuration(
                        main={"size": Resolutions.P720},
                        lores={"size": Resolutions.STREAM_16_9},
                    ),
                '1080p':
                    self.picam2.create_video_configuration(
                        main={"size": Resolutions.P1080},
                        lores={"size": Resolutions.STREAM_16_9},
                    ),
            }
            ,
            'still': 
                self.picam2.create_still_configuration()
        }          
            
    def __init__(self) -> None:
        self.picam2 = Picamera2()
        self.configurations = self._create_configurations()
        self.encoders = {'stream': MJPEGEncoder(bitrate=STREAM_BITRATE), 'record': H264Encoder()}
        self.streaming_output = StreamingOutput()
        self.picam2.configure(self.configurations["still"])
        self.video = Video()
        self.lock = Lock()        
    
    def _encoders_running(self) -> bool:
        return len(self.picam2.encoders) > 0
    
    def preview_running(self) -> bool:
        return self.encoders["stream"] in self.picam2.encoders
    def recording_running(self) -> bool:
        return self.encoders["record"] in self.picam2.encoders

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
        if self.recording_running():
            logging.warn("Recording already running.")
            return False
        stream_paused = False
        if self.preview_running():
            self.picam2.stop_encoder()
            logging.info("Stream paused.")
            stream_paused = True
            self.picam2.stop()

        logging.info(f"Configure to {resolution}")
        self.picam2.configure(self.configurations["video"][resolution])
        self.video.resolution = resolution
        self.video.quality = quality
        self._start_record_encoder()
        logging.info("Recording started.")
        if stream_paused:
            self._start_stream_encoder(lores=True)
            logging.info("Stream resumed.")
        self.picam2.start()

    def _recording_resume(self):
        logging.info(f"Configure to {self.video.resolution}")
        self.picam2.configure(self.configurations["video"][self.video.resolution])
        self._start_record_encoder()
        logging.info("Recording resumed.")

    def recording_stop(self) -> bool:
        if not self.recording_running():
            logging.warn("Recording not running.")
            return False
        stream_running = self.preview_running()
        self.picam2.stop_encoder()
        self.picam2.stop()

        logging.info("Recording stopped.")        

        if not stream_running:
            logging.info("Configure to still.")
            self.picam2.configure(self.configurations['still'])

        else:
            logging.info("Configure to preview.")
            self.picam2.configure(self.configurations['video']['240p'])
            self._start_stream_encoder()
            logging.info("Streaming resumed.")
            self.picam2.start()
        return True

    def recording_data(self) -> io.BytesIO:
        return self.video.release()    

    def capture_still(self) -> io.BytesIO:

        # If recording, pause recording and configure for still image.

        paused_encoders = self.picam2.encoders.copy()

        if self._encoders_running():
            self.picam2.stop_encoder()
            logging.info("Recording/streaming paused.")
            logging.info("Configure to still.")
            self.picam2.switch_mode(self.configurations['still'])
            logging.info(pformat(self.picam2.camera_configuration()))

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
       
    def capture_timelapse(self, interval : int, count : int):
        
        if self.recording_running():
            logging.warn("Timelapse cancelled: Recording running")
            return       
        
        # For some reason half framelimit length gives correct framerate. Dunno why.

        limit = 500000 * interval

        if interval < 1:
            config = self.picam2.create_video_configuration(
                main={"size": (1332, 990)},
                raw={"size": (1332, 990), "format": "SRGGB10_CSI2P"},
                buffer_count = 1,
                controls={'NoiseReductionMode': controls.draft.NoiseReductionModeEnum.Fast,                                  
                    'FrameDurationLimits': (limit, limit)}
            )
        else:
            config = self.picam2.create_still_configuration(
                main={"size": (2028, 1520)},
                controls={'FrameDurationLimits': (limit, limit)}
            )
       
        stream_paused = False
        if self.preview_running():
            self.picam2.stop_encoder()
            self.picam2.stop()
            stream_paused = True
            logging.info("Streaming paused.")            
                 
        logging.info("Configure to timelapse.") 
        self.picam2.configure(config)            
        self.picam2.start()
        data = []
        time.sleep(2)
        for i in range(count):
            data.append(self.capture_fast())
        self.picam2.stop() 
        if stream_paused:
            self._preview_resume()
            self.picam2.start()
        else:            
            self.picam2.configure(self.configurations['still']) 
            
        return data
             
    def capture_fast(self) -> io.BytesIO:    
        data = io.BytesIO()    
        self.picam2.capture_file(data, format='jpeg')
        return data


    def preview_start(self) -> bool:
        if self.preview_running():
            logging.warn("Stream already running.")
            return False        
        if not self.recording_running():
            logging.info("Configure to stream.")
            self.picam2.configure(self.configurations['video']['240p'])
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
            self.picam2.configure(self.configurations['video']['240p'])
            logging.info(pformat(self.picam2.camera_configuration()))
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
    

