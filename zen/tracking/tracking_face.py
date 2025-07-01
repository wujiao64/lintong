'''
Face Tracking with OpenCV and Pan-Tilt controled servos 
    Based on a face detection tutorial on pythonprogramming.net
    Visit original post: https://pythonprogramming.net/haar-cascade-face-eye-detection-python-opencv-tutorial/
Developed by Marcelo Rovai - MJRoBot.org @ 7Feb2018 
'''
import imutils
import numpy as np
import cv2
from UDPComms import Publisher


pub = Publisher(8830)
rx_ = 0.0
ry_ = 0.0
lx_ = 0.0
ly_ = 0.0
MESSAGE_RATE = 20

# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades
#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_eye.xml
#eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
capture = cv2.VideoCapture(0)
center_x=0
center_y=0

while 1:
    (grabbed, frame) = capture.read()
    height, width = frame.shape[0:2]
    screen_center = width / 2
    offset = 150
    if not grabbed:break

    msg = {
            "ly": 0,
            "lx": 0,
            "rx": 0,
            "ry": 0,
            "L2": 0,
            "R2": 0,
            "R1": 0,
            "L1": 0,
            "dpady": 0,
            "dpadx": 0,
            "x": 0,
            "square": 0,
            "circle": 0,
            "triangle": 0,
            "message_rate": MESSAGE_RATE,
    }

	# resize the frame, inverted ("vertical flip" w/ 180degrees),
	# blur it, and convert it to the HSV color space
    frame = imutils.resize(frame, width=600)
    #frame = imutils.rotate(frame, angle=180)
    #frame = cv2.flip(frame, -1)
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(hsv_frame, 1.3, 5)

    for (x,y,w,h) in faces:
        #servoPosition(int(x+w/2), int(y+h/2))
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = hsv_frame[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        #servoPosition(int(x+w/2), int(y+h/2))
        #center = (int(x+w/2), int(y+h/2))
        #print(center_x)
        center_x = int(x+w/2)
        center_y = int(y+h/2)
        #eyes = eye_cascade.detectMultiScale(roi_gray)
        #for (ex,ey,ew,eh) in eyes:
        #    cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

    # 简单的打印反馈数据，之后补充运动控制
    if center_x < screen_center - offset:
        print("turn left")
        ly_=0.5
    elif screen_center - offset <= center_x <= screen_center + offset:
        print(center_x)
    elif center_x > screen_center + offset:
        print("turn right")
        ly_=-0.5
    msg = {}
    msg["lx"] = lx_
    msg["ly"] = ly_
    msg["rx"] = rx_
    msg["ry"] = ry_
    msg["x"] = 0
    msg["square"] = 0
    msg["circle"] = 0
    msg["triangle"] = 0
    msg["dpady"] = 0
    msg["dpadx"] = 0
    msg["L1"] = 1
    msg["R1"] = 1
    msg["L2"] = 0
    msg["R2"] = 0
    msg["message_rate"] = MESSAGE_RATE
#   print(msg)
    pub.send(msg)

    cv2.imshow('Frame',frame)
    k = cv2.waitKey(30) & 0xff
    if k == 27: # press 'ESC' to quit
        break

# do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff \n")

capture.release()
cv2.destroyAllWindows()
