from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import cv2
import base64
from engineio.async_drivers import threading


app = Flask(__name__)
CORS(app, resources={r"/*":{"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

camera_state = False

def http_call():
    """return JSON with string data as the value"""
    data = {'data':'This text was fetched using an HTTP call to server on render'}
    return jsonify(data)

@socketio.on("connect")
def connected():
    print(request.sid)
    print("client has connected")

@socketio.on("switch")
def camera_switch(state):
    global camera_state
    if state is True:
        camera_state = True
        emit("switch", {"data": True})
    else:
        camera_state=False
        emit("switch", {"data": False})

@socketio.on("data")
def handle_message():
    global camera_state
    camera: cv2.VideoCapture = cv2.VideoCapture(0)
    try:
        while True:
            success, frame0 = camera.read()  # read the camera frame
            if success:
                ret, buffer = cv2.imencode('.jpg', frame0)
                stream = base64.b64encode(buffer.tobytes())
                emit("data",{"message": "data:image/jpg;base64,{0}".format(stream.decode('utf-8'))}, broadcast=True)
            if camera_state is False:
                camera.release()
                break
    except: 
        print("Problem with camera")
        

@socketio.on("disconnect")
def disconnected():
    print("user disconnected")
    # emit("disconnect", {"data": f"id: {request.sid} has disconnected"})

if __name__=="__main__":
    socketio.run(app, port=9928, allow_unsafe_werkzeug=True)