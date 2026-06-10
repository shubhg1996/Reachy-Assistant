# examples/capture_frame.py
import cv2
from iphone_cam import IPhoneCamera

if __name__ == "__main__":
    try:
        # Use the context manager to ensure the camera is released
        with IPhoneCamera() as cam:
            frame = cam.capture_frame()

            # Display the captured frame
            cv2.imshow("iPhone Camera Frame", frame)
            print("Frame captured! Press any key to close the window.")
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    except Exception as e:
        print(f"An error occurred: {e}")
