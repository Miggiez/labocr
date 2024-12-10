import cv2
import base64

def open_camera():
    camera: cv2.VideoCapture = cv2.VideoCapture(0) 
    while True:
        success, frame0 = camera.read()  # read the camera frame

        if success:
            ret, buffer = cv2.imencode('.jpg', frame0)
            stream = base64.b64encode(buffer.tobytes())
            print("data:image/jpg;base64,{0}".format(stream.decode('utf-8')))

        else:
            camera.release()
            break

open_camera()