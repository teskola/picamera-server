from client import client
from camera import instance as camera
import io

bucket = "raspberry"

# Configure for high-quality still picture, take picture

camera_config = camera.create_still_configuration()
camera.switch_mode(camera_config)
data = io.BytesIO()
camera.capture_file(data, format='jpeg')
camera.switch_mode(camera.create_video_configuration(main={"size": (640, 480)}))

# Change the stream position to start for Minio to get correct bytes

data.seek(0)

# Upload to Minio

result = client().put_object(
    bucket, "capture.jpg", data, len(data.getvalue()),
    content_type="image/jpg")


print(
    "created {0} object; etag: {1}".format(
        result.object_name, result.etag,
    ))
