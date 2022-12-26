import zmq
import base64
import numpy as np
import cv2
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://localhost:5555')
socket.setsockopt_string(zmq.SUBSCRIBE,np.unicode(''))
while True:
    try:
        frame = socket.recv_string()
        img = base64.b64decode(frame)
        npimg = np.frombuffer(img, dtype=np.uint8)
        source = cv2.imdecode(npimg, 1)
        cv2.imshow("image", source)
        cv2.waitKey(0)

    finally:
        pass