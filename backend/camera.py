import logging
import io
import sched
import time
from pprint import pformat
from threading import Condition, Lock, Thread
from libcamera import controls
from picamera2 import Picamera2, Metadata
from picamera2.encoders import MJPEGEncoder, H264Encoder
from picamera2.outputs import FileOutput

STREAM_BITRATE = 2400000
TIMELAPSE_INTERVAL = 20
scheduler = sched.scheduler(time.time, time.sleep)


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
    def __init__(self, limit, interval, full_res, name) -> None:
        self.limit = limit
        self.interval = interval
        self.full_res = full_res
        self.name = name
        self.count = 0
        self.event = None
    
    def start(self, capture, stop, upload):
        logging.info("Timelapse started.")
        self.event = scheduler.enter(1, 1, self.capture_and_upload, argument=(capture, stop, self.name, upload, ))
        scheduler.run()
    
    def keep_alive(self):
        return self.interval < TIMELAPSE_INTERVAL
    
    def stop(self, func):
        logging.info("Timelapse stopped.")
        if self.event in scheduler.queue:
            scheduler.cancel(self.event)                     
            func()
    
    def running(self):
        return self.event is not None and self.event in scheduler.queue
    
    def capture_and_upload(self, capture, stop, name : str, upload):
        if self.limit == 0 or self.count < self.limit:
            self.event = scheduler.enter(self.interval, 1, self.capture_and_upload, argument=(capture, stop, name, upload, ))    
        capture(upload, name, self.full_res, self.keep_alive())   
        self.count += 1 
        if self.limit != 0 and self.count == self.limit and self.keep_alive():
            self.stop(stop)


class Video:
    def __init__(self, resolution, quality) -> None:
        self.resolution = resolution
        self.quality = quality
        self.data = io.BytesIO()    
   
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
                    controls={"FrameDurationLimits": (33333, 33333)},
                    buffer_count = 6
                ),
                'full':
                   self.picam2.create_still_configuration(
                    main={"size": Resolutions.FULL},
                    lores={"size": Resolutions.STREAM_4_3},
                    controls={"FrameDurationLimits": (100000, 100000)},
                    buffer_count = 6
                   )               
                
            }                          
        }          
   
    def __init__(self) -> None:
        self.picam2 = Picamera2()        
        self.configurations = self._create_configurations()
        self.encoders = {'preview': MJPEGEncoder(bitrate=STREAM_BITRATE), 'video': H264Encoder()}
        self.streaming_output = StreamingOutput()
        self._configuration = self.picam2.configure(self.configurations["still"]["half"])
        self.video = None
        self.timelapse : Timelapse = None
        self.lock = Lock() 

    def configuration(self) -> str:
        return self._configuration["main"]["size"]
    
    def configure_still(self, full_res : bool = False):        
        if full_res:
            logging.info(f"Configure to: full resolution")
            self._configuration = self.picam2.configure(self.configurations["still"]["full"])
        else:
            logging.info(f"Configure to: half resolution")
            self._configuration = self.picam2.configure(self.configurations["still"]["half"])
    
    def configure_video(self, resolution):
        logging.info(f"Configure to: {resolution}")
        if resolution == '720p':
            self._configuration = self.picam2.configure(self.configurations["video"]["720p"])
        elif resolution == '1080p':
            self._configuration = self.picam2.configure(self.configurations["video"]["1080p"])
    
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
    
    def start(self, full_res : bool = False):        
        if full_res and self.preview_running():
            self.picam2.stop()
            self.configure_still(full_res=True)
            self.picam2.start()
        if not self.preview_running():
            self.picam2.start()
    
    def stop(self):
        self.picam2.stop_encoder()
        self.picam2.stop() 

    def timelapse_start(self, limit, interval, full_res, name, upload):
        if self.timelapse is not None and self.timelapse.running():
            logging.warn("Timelapse already running!")
        self.timelapse = Timelapse(
            limit=limit, 
            interval=interval, 
            full_res=full_res, 
            name=name).start( 
            capture=self.capture_still, 
            stop=self.timelapse_stop,
            upload=upload)
    
    def timelapse_stop(self):
        if self.timelapse is not None:
            self.timelapse.stop() 
        if self.recording_running():
            return
        if self.preview_running():
            if self.configuration == Resolutions.FULL:
                self.picam2.stop()
                self.configure_still()
                self.picam2.start()
        else:
            self.picam2.stop()
            if self.configuration == Resolutions.FULL:
                self.configure_still()
          

    def recording_start(self, resolution, quality) -> bool:
        if self.recording_running():
            logging.warn("Recording already running.")
            return False
        if self.timelapse is not None and self.timelapse.interval < TIMELAPSE_INTERVAL:
            logging.warn("Recording cancelled: Timelapse running.")
            return False
        stream_paused = False
        if self.preview_running():
            self.picam2.stop_encoder()
            logging.info("Stream paused.")
            stream_paused = True
            self.picam2.stop()
        self.configure_video(resolution=resolution)
        self.video = Video(resolution=resolution, quality=quality)        
        self._start_video_encoder()
        logging.info("Recording started.")
        if stream_paused:
            self._start_preview_encoder()
            logging.info("Stream resumed.")
        self.picam2.start()
        return True

    def _recording_resume(self):
        self.configure_video(self.video.resolution)
        self._start_video_encoder()
        logging.info("Recording resumed.")

    def recording_stop(self) -> io.BytesIO:
        if not self.recording_running():
            logging.warn("Recording not running.")
            return None
        stream_running = self.preview_running()
        self.picam2.stop_encoder()
        self.picam2.stop()
        logging.info("Recording stopped.")        
        self.configure_still()

        if stream_running:            
            self._start_preview_encoder()
            logging.info("Streaming resumed.")
            self.picam2.start()
        data = self.video.data
        data.seek(0)
        return data    

    # Pause video/stream if running. Configure to half/full still. Return paused encoders.

    def pause_encoders(self, full_res : bool = False) -> list:
        paused_encoders = self.picam2.encoders.copy()
        if self.recording_running():
            self.picam2.stop_encoder()
            self.picam2.stop()
            logging.info("Recording/streaming paused.")
            self.configure_still(full_res=full_res)
            self.picam2.start()
        else:
            if full_res:
                self.picam2.stop()
                self.configure_still(full_res=True)
                self.picam2.start()
        self.picam2.start()
        return paused_encoders
    
    def restart_paused_encoders(self, paused_encoders : list, full_res : bool = False):
        if self.encoders['video'] in paused_encoders:
            self.picam2.stop()
            self._recording_resume()
            if self.encoders["preview"] in paused_encoders:
                self._preview_resume()
            self.picam2.start()
        elif full_res:
            self.picam2.stop()
            self.configure_still()
            self.picam2.start()        
             
        
    def capture_still(self, upload, name, full_res : bool = False, keep_alive : bool = False) -> io.BytesIO:

        if not keep_alive:
            paused_encoders = self.pause_encoders(full_res=full_res)        
        Thread(target=self.capture_and_upload, args=(upload, name, )).start()
        if not keep_alive:
            self.restart_paused_encoders(paused_encoders=paused_encoders, full_res=full_res)

    def capture_and_upload(self, upload, name):
        data = io.BytesIO()
        request = self.picam2.capture_request()
        request.save("main", data, format='jpeg')
        request.release()
        data.seek(0)
        upload(data, name)       

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
        if not self.encoders["preview"] in self.picam2.encoders:
            logging.warn("Stream not running")
            return False

        self.picam2.stop_encoder(encoders=[self.encoders["preview"]])
        logging.info("Streaming stopped.")
        if not self._encoders_running():
            self.picam2.stop()            
        return True
    

