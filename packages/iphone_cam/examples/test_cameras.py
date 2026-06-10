# test_cameras.py
import cv2


def list_cameras():
    print("Scanning for cameras...")
    for i in range(5):  # try indices 0-4
        cap = cv2.VideoCapture(i, cv2.CAP_AVFOUNDATION)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"Camera index {i}: OK, frame shape {frame.shape}")
            else:
                print(f"Camera index {i}: Opened but read failed")
            cap.release()
        else:
            print(f"Camera index {i}: Cannot open")


if __name__ == "__main__":
    list_cameras()
