from collections import deque
import imutils
import cv2 as cv
from UDPComms import Publisher

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
    pub = Publisher(8830)
    rx_ = 0.0
    ry_ = 0.0
    lx_ = 0.0
    ly_ = 0.0
    MESSAGE_RATE = ""

    buffer=64
    pts = deque(maxlen=buffer)
    center_x=0
    center_y=0
    colorLower = (35, 43, 46)	#绿色
    colorUpper = (77, 255, 255)
    # 定义结构元素,结构元素的形状,     MORPH_RECT 矩形  ,MORPH_ELLIPSE 椭圆形,   MORPH_CROSS 十字型
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))

    capture = cv.VideoCapture(0)
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
        # 将图像转成HSV颜色空间
        hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        # 基于颜色的物体提取
        mask = cv.inRange(hsv_frame, colorLower, colorUpper)
        mask2 = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)  #开操作：先腐蚀再膨胀，主要应用在二值图像或灰度图像
        mask3 = cv.morphologyEx(mask2, cv.MORPH_CLOSE, kernel)  #闭操作：先膨胀再腐蚀
        # 找出面积最大的区域
        contours,hierarchy = cv.findContours(mask3, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        maxArea = 0
        maxIndex = 0
        for i, c in enumerate(contours):
            area = cv.contourArea(c)
            if area > maxArea:
                maxArea = area
                maxIndex = i
        # 绘制
        cv.drawContours(frame, contours, maxIndex, (255, 255, 0), 2)
        # 获取外切矩形
        if (contours!=[]):
            x, y, w, h = cv.boundingRect(contours[maxIndex])
        else: x, y, w, h = 300,300,0,0
        cv.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        # 获取中心像素点
        center_x = int(x + w/2)
        center_y = int(y + h/2)
        cv.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
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
#        print(msg)
        pub.send(msg)
        #cv.imshow("mask4", mask3)
        cv.imshow("frame", frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

# cleanup the camera and close any open windows
capture.release()
cv.destroyAllWindows()