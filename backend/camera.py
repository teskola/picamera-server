import logging
import io
import sched
import time
from pprint import pformat
from threading import Condition, Lock, Thread
from libcamera import controls
from picamera2 import Picamera2, Metadata
from picamera2.encoders import MJPEGEncoder, H264Encoder, Quality
from picamera2.outputs import FileOutput

STREAM_BITRATE = 2400000
KEEP_ALIVE_LIMIT = 60
scheduler = sched.scheduler(time.monotonic, time.sleep)

def quality_to_int(quality : Quality) -> int:
    if quality == Quality.VERY_LOW:
        return 1
    elif quality == Quality.LOW:
        return 2
    elif quality == Quality.MEDIUM:
        return 3
    elif quality == Quality.HIGH:
        return 4
    elif quality == Quality.VERY_HIGH:
        return 5

class Resolutions:
    FULL = (4056, 3040)
    HALF = (2028, 1520)
    LOW = (1332, 990)
    STREAM_16_9 = (426, 240)
    STREAM_4_3 = (320, 240)
    P480 = (640, 480)
    P720 = (1280, 720)
    P1080 = (1920, 1080)

class Still:
    def __init__(self, limit, interval, full_res, name) -> None:
        self.limit = limit
        self.interval = interval
        self.full_res = full_res
        self.name = name
        self.count = 0
        self.event = None
        self.started = 0
        self.stopped = 0
    
    def start(self, capture, stop, upload):
        logging.info("Still scheduler started.")
        self.event = scheduler.enter(1, 1, self.tick, argument=(capture, stop, self.name, upload, ))
        Thread(target=scheduler.run).start()        
    
    def keep_alive(self):
        return self.interval < KEEP_ALIVE_LIMIT
    
    def stop(self, func):
        logging.info("Still scheduler stopped.")
        self.stopped = time.time()
        if self.event in scheduler.queue:
            scheduler.cancel(self.event)                     
            func()
    
    def running(self):
        return self.event is not None and self.event in scheduler.queue
    
    def tick(self, capture, stop, name : str, upload):
        if self.limit == 0 or self.count < self.limit:
            self.event = scheduler.enter(self.interval, 1, self.tick, argument=(capture, stop, name, upload, ))
        if self.count == 0:
            self.started = time.time()    
        capture(upload, name, self.full_res, self.keep_alive())   
        self.count += 1 
        if self.limit != 0 and self.count == self.limit and self.keep_alive():
            self.stop(stop)


class Video:
    def __init__(self, resolution, quality) -> None:
        self.resolution = resolution
        self.quality = quality
        self.data = io.BytesIO() 
        self.started = 0
        self.stopped = 0  

    def size(self):
        return len(self.data.getvalue()) 
    
   
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
                    buffer_count = 6,
                ),
                'full':
                   self.picam2.create_still_configuration(
                    main={"size": Resolutions.FULL},
                    lores={"size": Resolutions.STREAM_4_3},
                    controls={"FrameDurationLimits": (100000, 100000)},
                    buffer_count = 6
                   )               
                
            },
            'timelapse': 
                self.picam2.create_still_configuration(
                    main={"size": Resolutions.LOW},
                    raw={"size": Resolutions.LOW,
                         "format": 'SRGGB10_CSI2P'},
                    controls={"FrameDurationLimits": (33333, 33333),
                              "NoiseReductionMode": controls.draft.NoiseReductionModeEnum.Minimal,
                              },
                              
                    buffer_count = 4
                ),
            'preview':
                self.picam2.create_preview_configuration(
                    main={"size": Resolutions.STREAM_4_3,
                          "format": "YUV420"},
                    lores={"size": Resolutions.STREAM_4_3},
                    controls={"FrameDurationLimits": (33333, 33333)},
                    display=None,
                    encode=None,
                    buffer_count = 6
                )
            
              
                                    
        }          
   
    def __init__(self) -> None:
        self.picam2 = Picamera2()        
        self.configurations = self._create_configurations()
        self.encoders = {'preview': MJPEGEncoder(bitrate=STREAM_BITRATE), 'video': H264Encoder()}
        self.streaming_output : StreamingOutput = StreamingOutput()
        self.video : Video = None
        self.still : Still = None
        self.lock = Lock()  

    def current_resolution(self):
        if self.picam2.camera_configuration() is None:
            return None
        return self.picam2.camera_configuration()["main"]["size"]   
    
    def timelapse_test(self):
        self.picam2.configure(self.configurations["timelapse"])
        logging.info(pformat(self.picam2.camera_configuration()))
        self.picam2.start()
        time.sleep(1)        
        started = time.time()
        for i in range (30):
            self.picam2.capture_array()
        stopped = time.time()
        logging.info(f"Time elapsed: {stopped - started}")
        
        

        
    
    def configure_still(self, full_res : bool = False):
        if self.recording_running():
            logging.warn("Recording video => Capturing lower resolution image.")                               
        elif full_res and self.current_resolution() != Resolutions.FULL:
            logging.info(f"Configure to: full resolution")
            self.picam2.stop()
            self.picam2.configure(self.configurations["still"]["full"])
        elif not full_res and self.current_resolution() != Resolutions.HALF:
            logging.info(f"Configure to: half resolution")
            self.picam2.stop()
            self.picam2.configure(self.configurations["still"]["half"])
        logging.info(pformat(self.picam2.camera_configuration()))
            
    
    def configure_video(self, resolution):
        logging.info(f"Configure to: {resolution}")
        if resolution == '720p' and self.current_resolution() != Resolutions.P720:
            self.picam2.stop()
            self.picam2.configure(self.configurations["video"]["720p"])
        elif resolution == '1080p' and self.current_resolution() != Resolutions.P1080:
            self.picam2.stop()
            self.picam2.configure(self.configurations["video"]["1080p"])
    
    def configure_preview(self):
        logging.info("Configure to preview.")
        self.picam2.stop()
        self.picam2.configure(self.configurations["preview"])
        logging.info(pformat(self.picam2.camera_configuration()))

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
        self.picam2.close()
    
    def running(self):
        return self._encoders_running() or (self.still is not None and self.still.running())
    
    def status(self):
        result = {}
        result["running"] = self.running()

        video = {}
        if self.video is not None:
            
            video = {
                'resolution': self.video.resolution,
                'quality': quality_to_int(self.video.quality),
                'started': self.video.started,
                'stopped': self.video.stopped,
                'size': self.video.size(),
                'running': self.recording_running()
            }

        still = {}
        if self.still is not None:
            still = {
                'limit': self.still.limit,
                'interval': self.still.interval,
                'full_res': self.still.full_res,
                'name': self.still.name,
                'count': self.still.count,
                'running': self.still.running(),
                'started': self.still.started,
                'stopped': self.still.stopped
            } 
         
        config = self.picam2.camera_configuration().copy()
        del config["controls"]
        del config["colour_space"]
        del config["transform"]
        result["configration"] = config
        result["video"] = video
        result["still"] = still
        return result

    def still_start(self, limit, interval, full_res, name, upload):
        if self.still is not None and self.still.running():
            logging.warn("Still scheduler already running!")
            return
        
        self.still = Still(
            limit=limit, 
            interval=interval, 
            full_res=full_res, 
            name=name)
        self.still.start(
            capture=self.capture_still, 
            stop=self.reconfig_after_stop,
            upload=upload)
    
    def reconfig_after_stop(self):
        if self.recording_running():
            return
        if self.preview_running():
            self.configure_preview()
            self.picam2.start()
        else:
            self.picam2.stop()
    
    def still_stop(self):
        if self.still is not None:
            self.still.stop(self.reconfig_after_stop) 
        
          

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
        self.configure_video(resolution=resolution)
        self.video = Video(resolution=resolution, quality=quality)        
        self._start_video_encoder()
        self.picam2.start()
        self.video.started = time.time()
        logging.info("Recording started.")
        if stream_paused:
            self._start_preview_encoder()
            logging.info("Stream resumed.")        
        return True   

    def recording_stop(self) -> io.BytesIO:
        if not self.recording_running():
            logging.warn("Recording not running.")
            return None
        stream_running = self.preview_running()
        self.picam2.stop_encoder()
        self.picam2.stop()
        self.video.stopped = time.time()
        logging.info("Recording stopped.")        
        self.configure_still()

        if stream_running:            
            self._start_preview_encoder()
            logging.info("Streaming resumed.")
            self.picam2.start()
        data = self.video.data
        data.seek(0)
        return data      
             
    def capture_still(self, upload, name, full_res : bool = False, keep_alive : bool = False) -> io.BytesIO:
        self.configure_still(full_res=full_res)
        self.picam2.start()
        Thread(target=self.capture_and_upload, args=(upload, name, )).start()
        if not keep_alive:
            self.reconfig_after_stop()

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
        if self.current_resolution() is None or not self.running():
            self.configure_preview()
        self._start_preview_encoder()
        self.picam2.start()
        logging.info("Streaming started.")            
        return True   

    def preview_stop(self) -> bool:
        if not self.encoders["preview"] in self.picam2.encoders:
            logging.warn("Stream not running")
            return False

        self.picam2.stop_encoder(encoders=[self.encoders["preview"]])
        logging.info("Streaming stopped.")
        if not self.running():
            self.picam2.stop()            
        return True
    

