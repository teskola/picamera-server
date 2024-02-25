import os
import io
import logging

from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv

class MinioClient:
    def __init__(self) -> None:
        load_dotenv()
        self.client = Minio(
            os.getenv("MINIO_IP"),
            access_key=os.getenv("ACCESS_KEY"),
            secret_key=os.getenv("SECRET_KEY"),
            secure=False
        )
        self.bucket = os.getenv("BUCKET")
    
    def upload_image(self, data : io.BytesIO, filename : str):
        try:
            result = self.client.put_object(
                self.bucket, filename + ".jpg", data, len(data.getvalue()),
                content_type="image/jpg")    
            logging.info("created %s object; etag: %s",
            result.object_name, result.etag)
        except S3Error as e:
            logging.error("Image upload failed: %s", str(e))
    
    def upload_video(self, data : io.BytesIO, filename : str):
        try:
            result = self.client.put_object(
                self.bucket, filename + ".h264", data, len(data.getvalue()),
                content_type="video/h264")
            logging.info("created %s object; etag: %s",
            result.object_name, result.etag)
            return result
        except S3Error as e:
            logging.error("Video upload failed: %s", str(e))
