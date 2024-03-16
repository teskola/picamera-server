import os
import io
import logging

from minio import Minio
from minio.error import S3Error
from minio.helpers import ObjectWriteResult
from dotenv import load_dotenv

class MinioClient:
    def result_dict(self, result : ObjectWriteResult):
        return {
                "bucket_name": result.bucket_name,
                "object_name": result.object_name,
                "version_id": result.version_id,
                "etag": result.etag,
                "last_modified": result.last_modified,
                "location": result.location}
    
    def __init__(self) -> None:
        load_dotenv()
        self.client = Minio(
            os.getenv("MINIO_IP"),
            access_key=os.getenv("ACCESS_KEY"),
            secret_key=os.getenv("SECRET_KEY"),
            secure=False
        )
        self.bucket = os.getenv("BUCKET")
    
    """ def upload_file(self, file):
        self.client.fput_object(self.bucket, 'raw.jpg', file)
     """

    def upload_image(self, data : io.BytesIO, filename : str):
        logging.info("Uploading image...")
        try:
            result = self.client.put_object(
                self.bucket, "/still/" + filename + ".jpg", data, len(data.getvalue()),
                content_type="image/jpg")    
            logging.info("created %s object; etag: %s",
            result.object_name, result.etag)            
            return self.result_dict(result)
        except S3Error as e:
            logging.error("Image upload failed: %s", str(e))
        finally:
            data.seek(0)
            data.truncate()
    
    def upload_video(self, data : io.BytesIO, filename : str, on_complete, args : str):
        # TODO: connection error
        # What happens if delete while uploading?
        # TODO: prevent multiple uploads of same data
        logging.info("Uploading video...")
        try:
            result = self.client.put_object(
                self.bucket, "/video/" + filename + ".h264", data, len(data.getvalue()),
                content_type="video/h264")
            logging.info("created %s object; etag: %s",
            result.object_name, result.etag)
            return self.result_dict(result)
        except S3Error as e:
            logging.error("Video upload failed: %s", str(e))
        finally:            
            on_complete(args)
    

