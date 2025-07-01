from UDPComms import Publisher
import cv2
from pyzbar import pyzbar

pub = Publisher(8830)
rx_ = 0.0
ry_ = 0.0
lx_ = 0.0
ly_ = 0.0
l_alpha = 0.15
r_alpha = 0.3
MESSAGE_RATE = ""
offset = 150
#二维码动态识别
camera=cv2.VideoCapture(0)
camera.set(3,640) #设置分辨率
camera.set(4,480)
while True:
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
    (grabbed,frame)=camera.read()
    #获取画面中心点
    height,width= frame.shape[0],frame.shape[1]
    screen_center = width / 2
    # 纠正畸变（这里把相机标定的代码去除了，各位自行标定吧）
    dst = frame
 
    # 扫描二维码
    text = pyzbar.decode(dst)
    for texts in text:
        #textdate = texts.data.decode('utf-8')
        #print(textdate)
        (x, y, w, h) = texts.rect#获取二维码的外接矩形顶点坐标
        #print('识别内容:'+textdate)
 
        # 二维码中心坐标
        center_x = int(x + w / 2)
        center_y = int(y + h / 2)
        cv2.circle(dst, (center_x, center_y), 2, (0, 255, 0), 8)  # 做出中心坐标
        #print('中间点坐标：',center_x,center_y)
        coordinate=(center_x,center_y)
        #在画面左上角写出二维码中心位置
        #cv2.putText(dst,'QRcode_location'+str(coordinate),(20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        #画出画面中心与二维码中心的连接线
        #cv2.line(dst, (center_x,center_y),(int(width/2),int(height/2)), (255, 0, 0), 2)
        #cv2.rectangle(dst, (x, y), (x + w, y + h), (0, 255, 255), 2)  # 做出外接矩形
        #二维码最小矩形
        cv2.line(dst, texts.polygon[0], texts.polygon[1], (255, 0, 0), 2)
        cv2.line(dst, texts.polygon[1], texts.polygon[2], (255, 0, 0), 2)
        cv2.line(dst, texts.polygon[2], texts.polygon[3], (255, 0, 0), 2)
        cv2.line(dst, texts.polygon[3], texts.polygon[0], (255, 0, 0), 2)
        #写出扫描内容
        #txt = '(' + texts.type + ')  ' + textdate
        #cv2.putText(dst, txt, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 50, 255), 2)
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
        pub.send(msg)
 
 
    cv2.imshow('dst',dst)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # 按q保存一张图片
        #cv2.imwrite("./frame.jpg", frame)
        break
 
camera.release()
cv2.destroyAllWindows()