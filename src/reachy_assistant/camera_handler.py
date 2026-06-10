import os
from datetime import datetime

import cv2
from iphone_cam import IPhoneCamera


class CameraHandler:
    def __init__(self, photos_dir="photos"):
        self.photos_dir = photos_dir
        os.makedirs(self.photos_dir, exist_ok=True)
        self.camera = IPhoneCamera()

    def take_picture(self):
        """Capture and save a photo. Returns (filepath, status_message)."""
        try:
            with self.camera as cam:
                frame = cam.capture_frame()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"photo_{timestamp}.jpg"
            filepath = os.path.join(self.photos_dir, filename)
            cv2.imwrite(filepath, frame)
            return filepath, f"Picture saved as {filename}"
        except Exception as e:
            return None, f"Failed to take picture: {e}"
