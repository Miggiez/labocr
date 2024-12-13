from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import cv2
import cvzone as z
import signal
import os
import numpy as np
import base64
from engineio.async_drivers import threading

class YOLOONNX:
    def __init__(self, model: str, classes: list[str] = None, nms: float = 0.5, score: float = 0.6):
        self.model = model
        self.classes = classes
        self.nms = nms
        self.score = score

    def bounding_boxes(self,img, combined_segment: list):
            
        combined_segment = sorted(combined_segment, key=lambda d: d['x'])
        names, x, y =[], [], []
        for j in combined_segment:
            if(j["name"] != "screen"):
                names.append(j["name"])
                x.append(j["x"])
                y.append(j["y"])

        word = ''.join([str(item) for item in names])
        if len(x) != 0 and len(y) != 0:
            # print(x[-1], y[-1])
            img, _ = z.putTextRect(img, f"{word}", (max(0, x[-1]), max(0, y[-1])), scale=2)
        
        return img, word

    def detect(self, img):
         # Load the ONNX model
        model: cv2.dnn.Net = cv2.dnn.readNetFromONNX(self.model)
        device_cuda = cv2.cuda.getCudaEnabledDeviceCount() 
        if device_cuda > 0:
            model.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            model.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        

        # Read the input image
        original_image: np.ndarray = img
        [height, width, _] = original_image.shape

        # Prepare a square image for inference
        length = max((height, width))
        image = np.zeros((length, length, 3), np.uint8)
        image[0:height, 0:width] = original_image

        # scale = length / 608

        # Preprocess the image and prepare blob for model
        blob = cv2.dnn.blobFromImage(image, scalefactor=1 / 255, size=(608, 608), swapRB=True)
        model.setInput(blob)

        # Perform inference
        outputs = model.forward()

        # Prepare output array
        outputs = np.array([cv2.transpose(outputs[0])])
        rows = outputs.shape[1]

        boxes = []
        scores = []
        class_ids = []
        combined_segment = []

        # Iterate through output to collect bounding boxes, confidence scores, and class IDs
        for i in range(rows):
            classes_scores = outputs[0][i][4:]
            
            (minScore, maxScore, minClassLoc, (x, maxClassIndex)) = cv2.minMaxLoc(classes_scores)
            if maxScore >= self.score:
                box = [
                    outputs[0][i][0] - (0.5 * outputs[0][i][2]),
                    outputs[0][i][1] - (0.5 * outputs[0][i][3]),
                    outputs[0][i][2],
                    outputs[0][i][3],
                ]
                boxes.append(box)
                scores.append(maxScore)
                class_ids.append(maxClassIndex)


        # Apply NMS (Non-maximum suppression)
        result_boxes = cv2.dnn.NMSBoxes(boxes, scores, self.score, self.nms, 0.5)

        # Iterate through NMS results to draw bounding boxes and labels
        for j in range(len(result_boxes)):
            index = result_boxes[j]
            box = boxes[index]
            i = {
                "class_id": class_ids[index],
                "class_name": self.classes[class_ids[index]],
                "confidence": scores[index],
                "box": box,
            }

            name, x1, y1 = i["class_name"], int(i["box"][0]*length), int(i["box"][1]*length) 
            w, h = int(i["box"][2]*length), int(i["box"][3]*length)

            combined_segment.append({'name': name, 'x': x1, 'y': y1})
            if name == "screen":
                z.cornerRect(img, (x1, y1, w, h))

        img, word = self.bounding_boxes(img=original_image, combined_segment=combined_segment)    
        
        return img, word
    

app = Flask(__name__)
CORS(app, resources={r"/*":{"origins": "*"}})
sio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

camera_state = False



class_ocr = [
    ".",
    "0",
    "0.", 
    "1", 
    "1.", 
    "2",
    "2.",
    "3",
    "3.",
    "4",
    "4.",
    "5",
    "5.",
    "6",
    "6.",
    "7",
    "7.",
    "8",
    "8.",
    "9",
    "9.",
    "A",
    "C",
    "V",
    "g",
    "screen",
]

result = YOLOONNX(model="/mnt/sda/projects/software/dapp/labocr/py/ocr.onnx", classes=class_ocr)

@app.route("/shutdown", methods=["GET"])
def shutdown():
    data = {"message": "Shutting Down!"}
    os.kill(os.getpid(), signal.SIGINT)
    return jsonify(data)

@sio.on("connect")
def connected():
    print(request.sid)
    print("Client has connected")

@sio.on("switch")
def camera_switch(state):
    global camera_state
    if state is True:
        camera_state = True
        emit("switch", {"data": True})
    else:
        camera_state=False
        emit("switch", {"data": False})

@sio.on("disconnect")
def disconnected():
    global camera_state
    camera_state = False
    print("Client has disconnected")

@sio.on("data")
def handle_message():
    global camera_state
    camera: cv2.VideoCapture = cv2.VideoCapture(0)
    try:
        while True:
            success, frame = camera.read()
            if success:
                img, word = result.detect(img=frame)
                ret, buffer = cv2.imencode(".jpg", img)
                stream = base64.b64encode(buffer.tobytes())
                emit("data", {"message": "data:image/jpg;base64,{0}".format(stream.decode('utf-8')), "val": f"{word}"},broadcast=True)
            if camera_state is False:
                camera.release()
                break
    except:
        print("Problem with camera")

if __name__ == "__main__":
    sio.run(app, port=9928, allow_unsafe_werkzeug=True)