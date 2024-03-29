import logging
import io
import sched
import time
from datetime import datetime
from pprint import pformat
from threading import Condition, Lock, Thread
from libcamera import controls
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder, H264Encoder, Quality
from picamera2.outputs import FileOutput

STREAM_BITRATE = 2400000
KEEP_ALIVE_LIMIT = 60
scheduler = sched.scheduler(time.time, time.sleep)


def insert_datetime(name : str) -> str:
    now = datetime.now()
    return name.replace('[YYYY]', str(now.year)).replace('[MM]', str(now.month)).replace('[DD]', str(now.date)).replace('[HH]', str(now.hour).zfill(2)).replace('[mm]', str(now.minute).zfill(2)).replace('[ss]', str(now.second).zfill(2))

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

def resolution_to_str(resolution : Resolutions) -> str:
    return f"{resolution[1]}p"

class Still:
    def __init__(self, limit, interval, full_res, name, notify) -> None:        
        self.name = name
        self.limit = limit
        self.interval = interval
        self.full_res = full_res
        self.count = 0
        self.event = None
        self.started = time.time()
        self.previous = None
        self.stopped = None
        self.notify = notify
    
    def fill(self):
        if self.limit > 0:
            return len(str(self.limit))
        return None
    
    def dict(self):
        return {
                'limit': self.limit,
                'interval': self.interval,
                'full_res': self.full_res,
                'name': self.name,
                'count': self.count,
                'running': self.running(),
                'started': self.started,
                'stopped': self.stopped,
                'previous': self.previous,
                'next': self.next()
            }
    
    def start(self, capture, stop, upload, delay : float = 1.0, epoch : float = None):
        if epoch is not None:               
            self.event = scheduler.enterabs(epoch, 1, self.tick, argument=(capture, stop, self.name, upload, ))    
        else:            
            self.event = scheduler.enter(delay, 1, self.tick, argument=(capture, stop, self.name, upload, ))
        logging.info(f"Still scheduler started.")
        Thread(target=scheduler.run).start()
    
    def keep_alive(self):
        return self.interval < KEEP_ALIVE_LIMIT
    
    def stop(self, func):
        logging.info("Still scheduler stopped.")
        self.stopped = time.time()
        if self.event in scheduler.queue:
            scheduler.cancel(self.event)                     
            func()
    
    def next(self):
        if self.running():
            return self.event.time
        return None
    
    def running(self):
        return self.event is not None and self.event in scheduler.queue
    
    def tick(self, capture, stop, name : str, upload):
        if self.limit == 0 or self.count < self.limit - 1:
            self.event = scheduler.enter(self.interval, 1, self.tick, argument=(capture, stop, name, upload, ))               
        self.count += 1 
        upload_name = insert_datetime(name)
        if self.fill() is None:
            upload_name = upload_name.replace('[count]', str(self.count))
        else:
            upload_name = upload_name.replace('[count]', str(self.count).zfill(self.fill()))
        capture(upload, upload_name, self.full_res, self.keep_alive())
        self.previous = time.time()   
        if self.limit != 0 and self.count == self.limit and self.keep_alive():
            self.stop(stop)
        self.notify()
        



class Video:
    def __init__(self, id : str, resolution : Resolutions, quality : Quality) -> None:
        self.id = id
        self.resolution = resolution
        self.quality = quality
        self.data = io.BytesIO() 
        self.started = None
        self.stopped = None

    def dict(self):
        return {
                "id": self.id,
                "resolution": resolution_to_str(self.resolution),
                "quality": quality_to_int(self.quality),
                "started": self.started,
                "stopped": self.stopped,
                "size": self.size(),
                "running": self.started is not None and self.stopped is None}
         

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
                        display=None,
                        encode=None
                    ),
                '720p':
                    self.picam2.create_video_configuration(
                        main={"size": Resolutions.P720},
                        lores={"size": Resolutions.STREAM_16_9},
                        display=None,
                        encode=None
                    ),
                '1080p':
                    self.picam2.create_video_configuration(
                        main={"size": Resolutions.P1080},
                        lores={"size": Resolutions.STREAM_16_9},
                        display=None,
                        encode=None
                    ),
            }
            ,
            'still': {
                'half':
                    self.picam2.create_still_configuration(
                    main={"size": Resolutions.HALF},
                    lores={"size": Resolutions.STREAM_4_3},
                    controls={"FrameDurationLimits": (33333, 33333)},
                    buffer_count = 4,
                    display=None,
                    encode=None
                ),
                'full':
                   self.picam2.create_still_configuration(
                    main={"size": Resolutions.FULL},
                    lores={"size": Resolutions.STREAM_4_3},
                    controls={"FrameDurationLimits": (100000, 100000)},
                    buffer_count = 4,
                    display=None,
                    encode=None
                   )               
                
            },
            'timelapse': 
                self.picam2.create_still_configuration(
                    main={"size": Resolutions.LOW},
                    raw={"size": Resolutions.LOW,
                         "format": 'SRGGB10_CSI2P'},
                    controls={"FrameDurationLimits": (10000, 10000),
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
                    buffer_count = 4
                )
            
              
                                    
        }          
   
    def __init__(self, condition : Condition, status : list) -> None:
        self.condition = condition
        self.status = status
        self.picam2 = Picamera2()        
        self.configurations = self._create_configurations()
        self.encoders = {'preview': MJPEGEncoder(bitrate=STREAM_BITRATE), 'video': H264Encoder()}
        self.streaming_output : StreamingOutput = StreamingOutput()
        self.videos : list[Video] = []
        self.still : Still = None
        self.lock = Lock()  
    
    def find_video_by_id(self, id: str) -> Video:
        for video in self.videos:
            if video.id == id:
                return video
        return None
    
    def find_recording_video(self) -> str:
        if not self.recording_running():
            return None
        for video in self.videos:
            if video.started is not None and video.stopped is None:
                return video.id
        raise LookupError('Recording video not found in videos list.')
        
    def notify_status_listeners(self):
        with self.condition:
            self.status.append(self.get_status())
            self.condition.notify_all()

    def current_resolution(self):
        if self.picam2.camera_configuration() is None:
            return None
        return self.picam2.camera_configuration()["main"]["size"]   
    
    def timelapse_test(self):
        self.picam2.configure(self.configurations["timelapse"])
        logging.info(pformat(self.picam2.camera_configuration()))
        self.picam2.start()
        time.sleep(1)     
        logging.info(pformat(self.get_status()))   
        logging.info(self.picam2.capture_metadata())
        """ started = time.time()
        for i in range (30):
            self.picam2.capture_array()
        stopped = time.time()
        logging.info(f"Time elapsed: {stopped - started}") """
        
        

        
    
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
            
    
    def configure_video(self, resolution : Resolutions):        
        if self.current_resolution() != resolution:            
            self.picam2.stop()
            res_str = resolution_to_str(resolution)
            logging.info(f"Configure to: {res_str}")
            self.picam2.configure(self.configurations["video"][res_str])            
    
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

    def _start_video_encoder(self, video):
        self.picam2.start_encoder(
            encoder=self.encoders['video'],
            output=FileOutput(video.data),
            quality=video.quality,
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
    
    def get_status(self):
        result = {"video": [],
                    "still": {},
                    "preview": {}}        
        result["running"] = self.picam2.started
        result["recording"] = self.recording_running()
        for video in self.videos:
            result["video"].append(video.dict())              
        if self.still is not None:
            result["still"] = self.still.dict()
        result["preview"] = {
            'running': self.preview_running(),
        }        
        return result
        
    def still_start(self, limit, interval, full_res, name, upload, delay : float = 1.0, epoch : int = None) -> dict:

        if self.still is not None and self.still.running():
            return {"error": {"running_error": "Still already running."}}
        
        self.still = Still(
            limit=limit, 
            interval=interval, 
            full_res=full_res, 
            name=name,
            notify=self.notify_status_listeners)
        self.still.start(            
            delay=delay,
            epoch=epoch,
            capture=self.capture_still, 
            stop=self.reconfig_after_stop,
            upload=upload)
        self.notify_status_listeners()
        return {}        
        
        
    def reconfig_after_stop(self):
        if self.recording_running():
            return
        if self.preview_running():
            self.configure_still()
            self.picam2.start()
        else:
            self.picam2.stop()
    
    def still_stop(self) -> dict:
        if self.still is None or not self.still.running():
            return {"error": {"running_error": "Still not running."}}
        else:
            self.still.stop(self.reconfig_after_stop) 
            self.notify_status_listeners()
            return  {}
         
    
    def delete_video(self, id: str):
        video = self.find_video_by_id(id)
        if video is None:
            return {"error": "Video not found.",
                    "id": id}
        if self.find_recording_video() == id:
            return {"error": {"running_error": "Video recording."},
                    "id": id}
        self.videos.remove(video)  
        del video   
        logging.info(f"Video deleted: {id}")
        self.notify_status_listeners()
        return {"id": id}
        

          

    def recording_start(self, id: str, resolution : Resolutions, quality : Quality) -> dict:        
        if self.recording_running():
            logging.warn("Recording already running.")
            return {"error": {"running_error": "Already recording."},
                    "id": id}
        preview_paused = False
        if self.preview_running():
            self.picam2.stop_encoder()
            logging.info("Preview paused.")
            preview_paused = True
            self.picam2.stop()
        self.configure_video(resolution=resolution)
        video = Video(id=id, resolution=resolution, quality=quality)
        self.videos.append(video)     
        self._start_video_encoder(video)
        self.picam2.start()
        video.started = time.time()
        logging.info(f"Started recording video: {video.id}")
        if preview_paused:
            self._start_preview_encoder()
            logging.info("Preview resumed.")   
        self.notify_status_listeners()     
        return {"id": id}
       

    def recording_stop(self) -> dict:
        if not self.recording_running():
            logging.warn("Recording not running.")
            return {"error": {"running_error": "Not recording."}}
        video = self.find_video_by_id(self.find_recording_video())
        preview_running = self.preview_running()
        self.picam2.stop_encoder()
        logging.info("Recording stopped.")      
        self.picam2.stop()
        video.stopped = time.time()
        video.data.seek(0)
        self.configure_still()

        if preview_running:            
            self._start_preview_encoder()
            logging.info("Preview resumed.")
            self.picam2.start()
        self.notify_status_listeners()
        return {}
             
             
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
            logging.warn("Preview already running.")
            return False
        if self.current_resolution() is None or not self.picam2.started:
            self.configure_still()
        self._start_preview_encoder()
        self.picam2.start()
        logging.info("Preview started.")       
        return True   

    def preview_stop(self) -> bool:
        if not self.encoders["preview"] in self.picam2.encoders:
            logging.warn("Preview not running")
            return False

        self.picam2.stop_encoder(encoders=[self.encoders["preview"]])
        logging.info("Preview stopped.")
        if not self.picam2.started:
            self.picam2.stop()   
        return True
    

