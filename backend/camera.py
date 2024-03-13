import logging
import io
import sched
import time
import traceback
from datetime import datetime
from pprint import pformat
from threading import Condition, Lock, Thread
from libcamera import controls
from picamera2 import Picamera2, Metadata
from picamera2.encoders import MJPEGEncoder, H264Encoder, Quality
from picamera2.outputs import FileOutput

STREAM_BITRATE = 2400000
KEEP_ALIVE_LIMIT = 60
scheduler = sched.scheduler(time.time, time.sleep)

def insert_datetime(name : str) -> str:
    now = datetime.now()
    return name.replace('[year]', str(now.year)).replace('[month]', str(now.month)).replace('[day]', str(now.date)).replace('[HH]', str(now.hour).zfill(2)).replace('[mm]', str(now.minute).zfill(2)).replace('[ss]', str(now.second).zfill(2))

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

class AlreadyRunningError (Exception):
    pass

class NotRunningError (Exception):
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

def resolution_to_str(resolution : Resolutions) -> str:
    return f"{resolution[1]}p"

class Still:
    def __init__(self, limit, interval, full_res, name) -> None:
        if not isinstance(limit, int):
            raise AttributeError(f'Limit not an integer: {str(limit)}')        
        if (limit < 0):
            raise ValueError('Negative limit.')
        self.limit = limit
        if not isinstance(interval, int):
            raise AttributeError(f'Interval not an integer: {str(interval)}')     
        elif (interval < 1):
            raise ValueError(f'Interval under 1.0: {str(interval)}')   
        elif (interval > 60 * 60 * 6):
            raise ValueError('Interval over 6 hours.')
        self.interval = interval
        if not isinstance(full_res, bool):
            raise AttributeError(f'Full_res not a boolean: {str(full_res)}')
        self.full_res = full_res
        if not isinstance(name, str):
            raise AttributeError(f'Name not a string: {str(name)}')
        self.name = name
        self.count = 0
        self.event = None
        self.started = 0
        self.stopped = 0
    
    def fill(self):
        if self.limit > 0:
            return len(str(self.limit))
        return None
    
    def status(self):
        return {
                'limit': self.limit,
                'interval': self.interval,
                'full_res': self.full_res,
                'name': self.name,
                'count': self.count,
                'running': self.running(),
                'started': self.started,
                'stopped': self.stopped
            }
    
    def start(self, capture, stop, upload, delay : float = 1.0, epoch : float = None):
        if epoch is not None:   
            if time.time() > epoch:
                raise ValueError('Scheduled time is in the past')
            self.event = scheduler.enterabs(epoch, 1, self.tick, argument=(capture, stop, self.name, upload, ))    
        else:
            if delay < 1.0:
                delay = 1.0
            self.event = scheduler.enter(delay, 1, self.tick, argument=(capture, stop, self.name, upload, ))
        logging.info("Still scheduler started.")
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
        self.count += 1 
        upload_name = insert_datetime(name)
        if self.fill() is None:
            upload_name = upload_name.replace('[count]', str(self.count))
        else:
            upload_name = upload_name.replace('[count]', str(self.count).zfill(self.fill()))
        capture(upload, upload_name, self.full_res, self.keep_alive())   
        if self.limit != 0 and self.count == self.limit and self.keep_alive():
            self.stop(stop)


class Video:
    def __init__(self, resolution : str, quality : int) -> None:
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
        logging.info(pformat(self.status()))   
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
        try:
            result = {"video": {},
                      "still": {},
                      "preview": {}}        
            result["running"] = self.running()
            result["video"]["running"] = self.recording_running()
            if self.video is not None:                    
                result["video"]['resolution'] = self.video.resolution,
                result["video"]['quality'] = quality_to_int(self.video.quality)
                result["video"]['started'] = self.video.started
                result["video"]['stopped'] = self.video.stopped
                result["video"]['size'] = self.video.size()              

            if self.still is not None:
                result["still"] = self.still.status()
                    
            result["preview"] = {
                'running': self.preview_running(),
            }

            if self.running():
                result["metadata"] = self.picam2.capture_metadata()
            
            if self.picam2.camera_configuration() is not None:
                config = self.picam2.camera_configuration().copy()
                del config["controls"]
                del config["colour_space"]
                del config["transform"]
                result["configration"] = config
            return result
        except Exception as e:
            traceback.print_exc()
            logging.error(str(e))
            return {"error": e}

    def still_start(self, limit, interval, full_res, name, upload, delay : float = 1.0, epoch : float = None) -> dict:
        try:

            if self.still is not None and self.still.running():
                logging.warn("Still scheduler already running!")            
                raise AlreadyRunningError
            
            self.still = Still(
                limit=limit, 
                interval=interval, 
                full_res=full_res, 
                name=name)
            self.still.start(
                delay=delay,
                epoch=epoch,
                capture=self.capture_still, 
                stop=self.reconfig_after_stop,
                upload=upload)
            return {"status": self.status()}
        except AttributeError as e:
            traceback.print_exc()
            return {"error": e,
                    "status": self.status()} 
        except ValueError as e:
            traceback.print_exc()
            return {"error": e,
                    "status": self.status()}    
        except AlreadyRunningError as e:
            traceback.print_exc()
            return {"error": e,
                    "status": self.status()}        
        except Exception as e:
            traceback.print_exc()
            logging.error(str(e))
            return {"error": e}    
    
    def reconfig_after_stop(self):
        if self.recording_running():
            return
        if self.preview_running():
            self.configure_still()
            self.picam2.start()
        else:
            self.picam2.stop()
    
    def still_stop(self) -> dict:
        try:
            if self.still is None:
                raise NotRunningError
            else:
                self.still.stop(self.reconfig_after_stop) 
                return  {"status": self.status()}
        except NotRunningError as e:
            return {"error": e,
                    "status": self.status()}
        except Exception as e:
            traceback.print_exc()
            logging.error(str(e))
            return {"error": e}
        
          

    def recording_start(self, resolution : Resolutions, quality : Quality) -> dict:        
        try:
            if self.recording_running():
                logging.warn("Recording already running.")
                raise AlreadyRunningError
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
            return {"status": self.status()}
        except AlreadyRunningError as e:
            return {"error": e,
                    "status": self.status()}
        except Exception as e:
            traceback.print_exc()
            logging.error(str(e))
            return {"error": e} 

    def recording_stop(self) -> dict:
        try:                
            if not self.recording_running():
                logging.warn("Recording not running.")
                raise NotRunningError
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
            return {"data": data,
                    "status": self.status()}
        except NotRunningError as e:
            return {"error": e,
                    "status": self.status()}
        except Exception as e:
            traceback.print_exc()
            logging.error(str(e))
            return {"error": e}
             
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
            self.configure_still()
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
    

