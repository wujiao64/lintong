# import the necessary packages
from collections import deque
import numpy as np
#import argparse
import imutils
import time
import cv2
import UDPComms
#from UDPComms import Publisher, Subscriber, timeout
#from State import BehaviorState, State
#from Command import Command


def direction_helper(trigger, opt1, opt2):
    if trigger == opt1:
        return -1
    if trigger == opt2:
        return 1
    return 0

def direction_helper(opt1, opt2):
    if opt1:
        return -1
    if opt2:
        return 1
    return 0

if __name__ == "__main__":
	# define the lower and upper boundaries of the "yellow object"
	# (or "ball") in the HSV color space, then initialize the
	# list of tracked points 色调（H），饱和度（S），亮度（V）
#    colorLower = (24, 100, 100) #黄色   
#    colorUpper = (44, 255, 255)
#    colorLower = (35, 43, 46) #绿色
#    colorUpper = (77, 255, 255)
    colorLower = (0,43,46) #红色
    colorUpper = (10,255,255)
    buffer=64
    pts = deque(maxlen=buffer)
    center_x=300
    center_y=300

    """
    state = State()
    state.activation=1
    
    command = Command()
    command.activate_event=True
    command.trot_event=True
    command.activation=1
    """
    pub = UDPComms.Publisher(8830)
    #udp_handle = UDPComms.Subscriber(8840, timeout=0.3)
    #msg_s = udp_handle.get()
    #if msg_s["L1"]==1 : print("L1=1")
    rx_ = 0.0
    ry_ = 0.0
    lx_ = 0.0
    ly_ = 0.0
    MESSAGE_RATE = 20
    dog_status = "stand"

    msg = {"ly": 0,"lx": 0, "rx": 0, "ry": 0, "L2": 0, "R2": 0, "R1": 0, "L1": 1, "dpady": 0, "dpadx": 0, "x": 0, "square": 0,
        "circle": 0, "triangle": 0, "message_rate": MESSAGE_RATE,}
    pub.send(msg)
    time.sleep(2)
    msg = {"ly": 0,"lx": 0, "rx": 0, "ry": 0, "L2": 0, "R2": 0, "R1": 1, "L1": 0, "dpady": 0, "dpadx": 0, "x": 0, "square": 0,
        "circle": 0, "triangle": 0, "message_rate": MESSAGE_RATE,}
    pub.send(msg)
    time.sleep(1)

    dog_status="step"
    print (dog_status)
    # 定义结构元素
    capture = cv2.VideoCapture(0)
    print(capture.isOpened())

    while True:
        (grabbed, frame) = capture.read()
        height, width = frame.shape[0:2]
        screen_center = width / 2
        offset = 150
		# if we are viewing a video and we did not grab a frame,
		# then we have reached the end of the video
        if not grabbed:break

        msg = {
            "ly": 0,"lx": 0,
            "rx": 0,"ry": 0,
            "L2": 0,"R2": 0,
            "R1": 0,"L1": 0,
            "dpady": 0,"dpadx": 0,
            "x": 0,"square": 0,"circle": 0,"triangle": 0,
            "message_rate": MESSAGE_RATE,
        }
		# resize the frame, inverted ("vertical flip" w/ 180degrees),
		# blur it, and convert it to the HSV color space
        frame = imutils.resize(frame, width=600)
        frame = imutils.rotate(frame, angle=180) #图像180度旋转
        # 将图像转成HSV颜色空间
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # 基于颜色的物体提取
		# construct a mask for the color "green", then perform
		# a series of dilations and erosions to remove any small
		# blobs left in the mask
        mask = cv2.inRange(hsv_frame, colorLower, colorUpper)
        mask = cv2.erode(mask, None, iterations=2) #侵蚀的作用：对象边缘减少一个像素,对象边缘平滑,弱化了对象与对象之间连接
        mask = cv2.dilate(mask, None, iterations=2) #膨胀的作用：对象边缘增加一个像素,使对象边缘平滑,减少了对象与对象之间的距离
        # 找出面积最大的区域
		# find contours in the mask and initialize the current
		# (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None
 
		# only proceed if at least one contour was found
        if len(cnts) > 0:
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle and
			# centroid
            # 获取中心像素点
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            #center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            center_x = int(M["m10"] / M["m00"])
            center_y = int(M["m01"] / M["m00"])
            #print(center_x)

			# only proceed if the radius meets a minimum size
            if radius > 50:
				# draw the circle and centroid on the frame,
				# then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)

		# update the points queue
        pts.appendleft(center)
		
		# loop over the set of tracked points
        for i in range(1, len(pts)):
			# if either of the tracked points are None, ignore
			# them
            if pts[i - 1] is None or pts[i] is None:
                continue

			# otherwise, compute the thickness of the line and
			# draw the connecting lines
            #thickness = int(np.sqrt(buffer / float(i + 1)) * 2.5)
            #cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)


        # 简单的打印反馈数据，之后补充运动控制
        rx_=0
        if 10<center_x < screen_center - offset:
            print("turn left")
            rx_=-0.9
            #ly_=0.5
        elif screen_center - offset <= center_x <= screen_center + offset:
            rx_=0
            #ly_=0.5
            #print(center_x)
        elif 590 > center_x > screen_center + offset:
            print("turn right")
            rx_=0.9
            #ly_=0.5
        
        if center_y<10 or center_y>420 : rx_=0
        
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
        msg["L1"] = 0
        msg["R1"] = 0
        msg["L2"] = 0
        msg["R2"] = 0
        msg["message_rate"] = MESSAGE_RATE
#        print(msg)
        pub.send(msg)
        time.sleep(1 / MESSAGE_RATE)
        cv2.waitKey(1)

		# show the frame to our screen
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # 按q
            break

# cleanup the camera and close any open windows
capture.release()
cv2.destroyAllWindows()