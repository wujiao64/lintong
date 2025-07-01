import numpy as np
import imutils

from collections import deque
import time
import cv2
import UDPComms



def sign(x):
    if x>0:
        return 1.0
    else:
        return -1.0


def change_direct(temp):
    """改变方向函数"""
    if temp > 250:
        print("转圈寻找")
        return 0
        
        
    elif temp > 0:
        print("左转")
        return -1
        
        
        
    else:
        print("右转")
        return 1
        



"""def trace_fun():

    cap = cv2.VideoCapture(-1)
    result = None
    while(cap.isOpened()):
        msg = {
                "ly": 0,"lx": 0,
                "rx": 0,"ry": 0,
                "L2": 0,"R2": 0,
                "R1": 0,"L1": 0,
                "dpady": 0,"dpadx": 0,
                "x": 0,"square": 0,"circle": 0,"triangle": 0,
                "message_rate": MESSAGE_RATE,
            }
        # Capture frame-by-frame
        ret, frame = cap.read()
        # 真实图
        # cv2.imshow('real_img', frame)
        # 转化为灰度图
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # cv2.imshow("gray_img", gray)
        # 大津法二值化
        retval, dst = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
        # cv2.imshow("dst_img", dst)

        # 单单看第240行的像素
        color = dst[400]
        # 找到白色的像素点个数
        white_count = np.sum(color == 255)
        # 找到白色的像素点索引
        white_index = np.where(color == 255)
        # 防止white_count=0的报错
        if white_count == 0:
            continue
        # 找到白色像素的中心点位置
        center = (white_index[0][white_count - 1] + white_index[0][0]) / 2
        # 计算出center与标准中心点的偏移量,因为摄像头的像素为：480x640,宽度的一半
        direction = center - 320
        # 画线 图像，起点坐标，终点坐标，线的颜色， 线的大小
        cv2.line(frame, (320, 120), (320, 350), (0, 255, 0), 1, 4)
        cv2.line(frame, (300, 200), (300, 280), (0, 255, 0), 1, 4)
        cv2.line(frame, (340, 200), (340, 280), (0, 255, 0), 1, 4)
        print(direction)
        cv2.line(frame, (int(center), 200), (int(center), 280), (0, 0, 255), 1, 4)
        # 添加文字  图像，文字内容， 坐标 ，字体，大小，颜色，字体厚度
        cv2.putText(frame, 'distance:%s' % direction, (int(center)-40, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv2.imshow("frame", frame)
        # 判断方向的下一步操作
        result = change_direct(direction)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()"""


if __name__ == '__main__':

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
    
    
    
    # center定义
    center = 320
    cap = cv2.VideoCapture(0)
    result = None
    # PID 初始数据
    error = [0.0] * 3
    adjust = [0.0] * 3
    # PID 参数配置
    kp = 1.1
    ki = 0.3
    kd = 0.1
    target = 320

    while(1):
        # Capture frame-by-frame
        ret, frame = cap.read()
        # 真实图
        # cv2.imshow('real_img', frame)
        # 转化为灰度图
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # cv2.imshow("gray_img", gray)
        # 大津法二值化
        retval, dst = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
        # 膨胀，白区域变大
        dst = cv2.dilate(dst, None, iterations=2)
        # 单单看第240行的像素
        color = dst[400]
        # 找到白色的像素点个数
        white_count = np.sum(color == 255)
        # 找到白色的像素点索引
        white_index = np.where(color == 255)
        # 防止white_count=0的报错
        if white_count == 0:
            white_count = 1
        # 找到白色像素的中心点位置
        #center = (white_index[0][white_count - 1] + white_index[0][0]) / 2
        # 找到黑色像素的中心点位置
        center_now = (white_index[0][white_count - 1] + white_index[0][0]) / 2

        # 计算出center与标准中心点的偏移量,因为摄像头的像素为：480x640,宽度的一半
        direction = center_now - 320
        # 画线 图像，起点坐标，终点坐标，线的颜色， 线的大小
        #cv2.line(frame, (320, 120), (320, 350), (0, 255, 0), 1, 4)
        #cv2.line(frame, (300, 200), (300, 280), (0, 255, 0), 1, 4)
        #cv2.line(frame, (340, 200), (340, 280), (0, 255, 0), 1, 4)
        print(direction)
        #cv2.line(frame, (int(center), 200), (int(center), 280), (0, 0, 255), 1, 4)
        # 添加文字  图像，文字内容， 坐标 ，字体，大小，颜色，字体厚度
        #cv2.putText(frame, 'distance:%s' % direction, (int(center)-40, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)  
        # 判断方向的下一步操作
        # 停止
        if abs(direction) > 250:
            rx_=0

        # 更新PID误差
        error[0] = error[1]
        error[1] = error[2]
        error[2] = center_now - target

        # 更新PID输出（增量式PID表达式）
        adjust[0] = adjust[1]
        adjust[1] = adjust[2]
        # adjust(k+2) = adjust(k+1) + kp * (e(k+2) - e(k+1)) + ki * e(k+2) + kd * (e(k+2)-2*e(k+1)+e(k))
        adjust[2] = adjust[1] \
            + kp*(error[2] - error[1]) \
            + ki*error[2] \
            + kd*(error[2] - 2*error[1] + error[0]); 

        # 饱和输出限制在70绝对值之内
        if abs(adjust[2]) > 70:
            adjust[2] = sign(adjust[2]) * 70

        # 执行PID

        # 右转
        elif adjust[2] >= 0:
            rx_=-0.8
        # 左转
        elif adjust[2] < -0:
            rx_=0.8

        msg = {}
        msg["lx"] = lx_
        msg["ly"] =0.8
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
        pub.send(msg)
        time.sleep(1 / MESSAGE_RATE)

        #frame = imutils.rotate(frame, angle=180) #图像180度旋转
        #cv2.imshow("frame", frame)
        # show the frame to our screen
        if cv2.waitKey(1) & 0xFF == ord('q'):  # 按q
            break



# cleanup the camera and close any open windows
cap.release()
cv2.destroyAllWindows()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    