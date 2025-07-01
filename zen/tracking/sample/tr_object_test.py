import cv2 as cv
# 定义结构元素
kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
# print kernel
capture = cv.VideoCapture(0)		
print(capture.isOpened())
ok, frame = capture.read()
lower_b = (65, 43, 46)
upper_b = (110, 255, 255)
height, width = frame.shape[0:2]
screen_center = width / 2
offset = 50
while ok:
    # 将图像转成HSV颜色空间
    hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    # 基于颜色的物体提取
    mask = cv.inRange(hsv_frame, lower_b, upper_b)
    mask2 = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
    mask3 = cv.morphologyEx(mask2, cv.MORPH_CLOSE, kernel)  
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
    else: x, y, w, h = 0,0,0,0
    cv.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    # 获取中心像素点
    center_x = int(x + w/2)
    center_y = int(y + h/2)
    cv.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
    # 简单的打印反馈数据，之后补充运动控制
    if center_x < screen_center - offset:
        print("turn left")
    elif screen_center - offset <= center_x <= screen_center + offset:
        print("keep")
    elif center_x > screen_center + offset:
        print("turn right")
    cv.imshow("mask4", mask3)
    cv.imshow("frame", frame)
    cv.waitKey(1)
    ok, frame = capture.read()
