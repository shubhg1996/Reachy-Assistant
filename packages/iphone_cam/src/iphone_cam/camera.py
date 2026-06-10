# src/iphone_cam/camera.py
import os
import platform

import cv2


class IPhoneCamera:
    def __init__(self, camera_index=None):
        """
        Args:
            camera_index: Optional camera index. If None, auto‑detect.
        """
        self.camera_index = camera_index
        self.cap = None
        self._apply_info_plist_fix()

    def _apply_info_plist_fix(self):
        if platform.system() != "Darwin":
            return
        current_dir = os.path.dirname(os.path.abspath(__file__))
        plist_path = os.path.join(current_dir, "info.plist")
        if os.path.exists(plist_path):
            os.environ["RESOURCEPATH"] = current_dir
        else:
            print(f"Warning: info.plist not found at {plist_path}")

    def _find_working_camera(self):
        """Try indices 0-4 to find a camera that can capture a frame."""
        for i in range(5):
            cap = cv2.VideoCapture(i, cv2.CAP_AVFOUNDATION)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret:
                    print(f"Found working camera at index {i}")
                    return i
        return None

    def capture_frame(self):
        if self.cap is None:
            index = self.camera_index
            if index is None:
                index = self._find_working_camera()
                if index is None:
                    raise RuntimeError("No working camera found.")
                self.camera_index = index

            self.cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
            if not self.cap.isOpened():
                raise RuntimeError(f"Could not open camera index {index}")

            # Optionally set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            # Discard the first (often black) frame to allow stream to start
            self.cap.grab()
            ret, _ = self.cap.retrieve()
            if not ret:
                raise RuntimeError("Camera warm-up failed.")

        # Now capture a usable frame
        self.cap.grab()
        ret, frame = self.cap.retrieve()
        if not ret:
            raise RuntimeError("Failed to capture frame.")
        return frame

    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.release()
