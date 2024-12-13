import cv2
import numpy as np
import cvzone as z

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
            z.putTextRect(img, f"{word}", (max(0, x[-1]), max(0, y[-1])), scale=1)

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

        self.bounding_boxes(img=original_image, combined_segment=combined_segment)    
        
            

        return original_image


classNames_ocr = [
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
    "screen"
]


cam = cv2.VideoCapture(0)
result = YOLOONNX("/mnt/sda/projects/software/dapp/labocr/py/ocr.onnx", classes=classNames_ocr)
while True:
    success, frame = cam.read()
    if success: 
        img = result.detect(img=frame)
        cv2.imshow("main", img)

        if cv2.waitKey(1) == ord("q"):
            break

cam.release()
cv2.destroyAllWindows() 
    