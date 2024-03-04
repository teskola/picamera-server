import logging
import io
import time
import copy
from pprint import pformat
from threading import Condition, Lock, Thread
from libcamera import controls
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder, H264Encoder
from picamera2.outputs import FileOutput

STREAM_BITRATE = 2400000

def interval_to_fps(interval):
    pass 

class Resolutions:
    FULL = (4056, 3040)
    HALF = (2028, 1520)
    LOW = (1332, 990)
    STREAM_16_9 = (426, 240)
    STREAM_4_3 = (320, 240)
    P480 = (640, 480)
    P720 = (1280, 720)
    P1080 = (1920, 1080)

class Timelapse:
    def __init__(self, resolution : int, interval: int, count : int, start) -> None:
        self.resolution = resolution
        self.interval = interval
        self.count = count
        self.start = start
    
    def start(self):
        self.start()

class Video:
    def __init__(self, resolution, quality) -> None:
        self.resolution = resolution
        self.quality = quality
        self.data = io.BytesIO()

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
            'still': {
                'half':
                    self.picam2.create_still_configuration(
                    main={"size": Resolutions.HALF},
                    lores={"size": Resolutions.STREAM_4_3},
                    buffer_count = 6
                ),
                'full':
                   self.picam2.create_still_configuration(
                    main={"size": Resolutions.FULL},
                    lores={"size": Resolutions.STREAM_4_3},
                    buffer_count = 6
                   )               
                
            }                          
        }          
            
    def __init__(self) -> None:
        self.picam2 = Picamera2()
        self.framecount = 0
        self.configurations = self._create_configurations()
        self.encoders = {'preview': MJPEGEncoder(bitrate=STREAM_BITRATE), 'video': H264Encoder()}
        self.streaming_output = StreamingOutput()
        self.picam2.configure(self.configurations["still"]["half"])
        self.video = None
        self.timelapse = None
        self.lock = Lock()        
    
    def _encoders_running(self) -> bool:
        return len(self.picam2.encoders) > 0
    
    def preview_running(self) -> bool:
        return self.encoders["preview"] in self.picam2.encoders
    def recording_running(self) -> bool:
        return self.encoders["video"] in self.picam2.encoders

    def _start_video_encoder(self):
        self.picam2.start_encoder(
            encoder=self.encoders['video'],
            output=FileOutput(self.video.data),
            quality=self.video.quality,
            name="main"
        )

    def _start_preview_encoder(self):
        self.picam2.start_encoder(
            encoder=self.encoders["preview"],
            output=FileOutput(self.streaming_output),
            name="lores"
        )

    def stop(self):
        self.picam2.stop_encoder()
        self.picam2.stop()
    
    def timelapse_start(self, resolution, interval, count) -> bool:
        if self.timelapse is not None:
            return False
        self.timelapse = Timelapse(resolution, interval, count)
        

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
        self._start_video_encoder()
        logging.info("Recording started.")
        if stream_paused:
            self._start_preview_encoder()
            logging.info("Stream resumed.")
        self.picam2.start()

    def _recording_resume(self):
        logging.info(f"Configure to {self.video.resolution}")
        self.picam2.configure(self.configurations["video"][self.video.resolution])
        self._start_video_encoder()
        logging.info("Recording resumed.")

    def recording_stop(self) -> bool:
        if not self.recording_running():
            logging.warn("Recording not running.")
            return False
        stream_running = self.preview_running()
        self.picam2.stop_encoder()
        self.picam2.stop()
        logging.info("Recording stopped.")        
        logging.info("Configure to still.")
        self.picam2.configure(self.configurations['still']['half'])

        if stream_running:            
            self._start_preview_encoder()
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
            self.picam2.switch_mode(self.configurations['still']['full'])
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
       
    def capture_timelapse(self, lock : Lock, upload, interval : int, count : int):
        
        if self.recording_running():
            logging.warn("Timelapse cancelled: Recording running")
            return        
       
        stream_paused = False
        if self.preview_running():
            self.picam2.stop_encoder()
            self.picam2.stop()
            stream_paused = True
            logging.info("Streaming paused.")            
                 
        
        if stream_paused:
            self._start_preview_encoder()
            logging.info("Streaming resumed.")
        self.picam2.start()
        lock.release()
        i = 0
        frame = 0
        data = [io.BytesIO()] * count
        while i < count:
            frame += 1
            logging.info(f"Frame: {frame}")
            if ((frame % (interval * 10)) == 0):
                data[i] = self.capture_fast()
                Thread(target=upload, args=(data[i], f'timelapse/capture{i}',)).start()
                i += 1
        if stream_paused:
            self.picam2.stop_encoder()
            logging.info("Streaming paused.")
        self.picam2.stop() 
        if stream_paused:
            self._preview_resume()
            self.picam2.start()
                    
             
    def capture_fast(self) -> io.BytesIO:    
        data = io.BytesIO()    
        self.picam2.capture_file(data, format='jpeg')
        data.seek(0)
        return data


    def preview_start(self) -> bool:
        if self.preview_running():
            logging.warn("Stream already running.")
            return False        
        if not self.recording_running():            
            self._start_preview_encoder()
            logging.info("Streaming started.")
            self.picam2.start()
        else:
            self._start_preview_encoder()
            logging.info("Streaming started.")
        return True

    def _preview_resume(self):        
        self._start_preview_encoder()
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
            self.picam2.configure(self.configurations['still']['half'])
        return True
    

