# -*- coding: utf-8 -*-
import io
import os
import time
import fcntl
import socket
import struct
#import picamera
import threading
from zen.Thread import *
from zen.Control import *
import imutils
import cv2
import numpy as np
from collections import deque
import traceback


class Server:
    def __init__(self):
        self.tcp_flag=False
        self.control=Control()
        self.cmd=COMMAND()
        self.battery_voltage=[8.4,8.4,8.4,8.4,8.4]

        self.tracking_face = True
        self.tracking_eyes = True
        self.tracking_ball = False

    def get_host_ip(self):
        try:
            s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            s.connect(('8.8.8.8',80))
            ip = s.getsockname()[0]
        except Exception as e:
            print(e)
            return "127.0.0.1"
        finally:
            s.close()
        return ip

    def get_interface_ip(self,ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', bytes(ifname[:15],'utf-8'))     #python3
                #struct.pack('256s', ifname[:15])                   #python2
                )[20:24])
        except Exception as e:
            print(e)
            return "no wifi"

    def turn_on_server(self):
        #ip adress
        HOST=self.get_interface_ip('wlan0')
        #Port 8000 for video transmission
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
        self.server_socket.bind((HOST, 8001))              
        self.server_socket.listen(5)
        
        #Port 5000 is used for instruction sending and receiving
        self.server_socket1 = socket.socket()
        self.server_socket1.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
        self.server_socket1.bind((HOST, 5001))
        self.server_socket1.listen(1)
        print('Server address: '+HOST)
        

    def turn_off_server(self):
        try:
            self.connection.close()
            self.connection1.close()
            stop_thread(self.control.Thread_conditiona)
        except :
            print ('\n'+"No client connection")
    
    def reset_server(self):
        self.turn_off_server()
        self.turn_on_server()
        self.video=threading.Thread(target=self.transmission_video)
        self.instruction=threading.Thread(target=self.receive_instruction)
        self.video.start()
        self.instruction.start()

    def send_data(self,connect,data):
        try:
            connect.send(data.encode('utf-8'))
            #print("send",data)
        except Exception as e:
            print(e)

    def transmission_video(self):
        try:
            self.connection,self.client_address = self.server_socket.accept()
            #self.connection=self.connection.makefile('wb')
            print ("video connection ... !")
        except Exception as e:
            print("video server socket error:",e)
            #traceback.print_exc()
            pass
        self.server_socket.close()
        try:
            print ("Start video transmit ... ")
            self.img_quality = 50    #  0~100
            self.resolution = (640,480)
            camera = cv2.VideoCapture(0)  #,cv2.CAP_GSTREAMER
            #print('isOpened:', camera.isOpened())
            encode_param=[int(cv2.IMWRITE_JPEG_QUALITY), self.img_quality]
            if self.tracking_face: FaceCascade = cv2.CascadeClassifier('./zen/haarcascade_frontalface_default.xml')
            if self.tracking_eyes: EyeCascade = cv2.CascadeClassifier('./zen/haarcascade_eye.xml')
            scalar = 8
            while(1): #while camera.isOpened():
                try:
                    #time.sleep(0.13)
                    (grabbed, frame)  = camera.read()
                    if not grabbed:
                        print('video end')
                        break
                    height, width, _ = frame.shape
                    # 对每一帧图片做大小处理　和大小的压缩
                    frame_small  = cv2.resize(frame, (int(width / scalar), int(height / scalar)), interpolation=cv2.INTER_CUBIC)    
                                   #cv2.resize(frame,self.resolution)
                    if self.tracking_face:
                        gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
                        faces = FaceCascade.detectMultiScale(
                                       gray,
                                       scaleFactor=1.1,
                                       minNeighbors=5
                        )
                        for (x, y, w, h) in faces:
                            x *= scalar
                            y *= scalar
                            w *= scalar
                            h *= scalar
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
                            face_roi = frame[y:y + int(h / 2), x:x + w]
                            face_gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

                            if self.tracking_eyes:
                                eyes = EyeCascade.detectMultiScale(
                                    face_gray,
                                    scaleFactor=1.1,
                                    minNeighbors=5
                                )

                                for (ex, ey, ew, eh) in eyes:
                                    cv2.rectangle(frame, (ex + x, ey + y), (ex + x + ew, ey + y + eh), (0, 0, 255), 4)

                    if self.tracking_ball:
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
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
                        # 基于颜色的物体提取
		                # construct a mask for the color "green", then perform
		                # a series of dilations and erosions to remove any small
		                # blobs left in the mask
                        mask = cv2.inRange(gray, colorLower, colorUpper)
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
                    
                    cv2.imshow('Video', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        #camera.release()
                        cv2.destroyAllWindows()
                        #break

                    result, imgencode = cv2.imencode('.jpg', frame, encode_param)    # 参1图片后缀名 参2 原图片的数据 参3图片质量 0-100 越大越清晰
                    # imgencode 是被压缩后的数据 无法正常显示     
                    img_code = np.array(imgencode)        # 转换为numpy格式数据
                    self.imgdata  = img_code.tostring()       # 转为二进制数据
                    # 发送的数据  大小 宽 高 图片数据
                    # 数据打包变为二进制
                    # pack方法参数1 指定打包数据的数据大小  i 4字节 h代表2字节
                    self.connection.send(struct.pack("<L",len(self.imgdata))+self.imgdata)
                    #发送图片信息(图片长度,分辨率,图片内容)self.resolution[0],self.resolution[1])+
                    time.sleep(0.01)
                except BaseException as e:
                    print ("video sent error:",e)
                    print ("End transmit ... " ) 
                    #traceback.print_exc()
                    camera.release()
                    self.reset_server()
                    return
                    #break

        except BaseException as e:
            print("camera error:",e)
            print ("Camera unintall")
            #traceback.print_exc()

    def sednRelaxFlag(self):
        if self.control.move_flag!=2:
            command=self.cmd.CMD_RELAX+"#"+str(self.control.move_flag)+"\n"
            self.send_data(self.connection1,command)
            self.control.move_flag= 2  
                  
    def receive_instruction(self):
        try:
            self.connection1,self.client_address1 = self.server_socket1.accept()
            print ("Client connection...!")
            self.control.Thread_conditiona.start()
            print ("control joystick_pub start ...")
        except Exception as e:
            print("client server socket error:",e)
            print ("Client connect failed")
        self.server_socket1.close()
        while True:
            try:
                allData=self.connection1.recv(1024).decode('utf-8')
                #allData=allData.strip("CMD_WORKING_TIME#")
                #allData=allData.strip("CMD_POWER#")
                #allData=allData.strip("CMD_SONIC#")
                #print(allData)
            except:
                if self.tcp_flag:
                    self.reset_server()  ##########################
                    break
                else:
                    break
            
            if allData=="" and self.tcp_flag:
                self.reset_server()
                break
            else:
                cmdArray=allData.split('\n')
                #print(cmdArray)
                if cmdArray[-1] !="":
                    cmdArray==cmdArray[:-1]
            
            for oneCmd in cmdArray:
                data=oneCmd.split("#")
                if data==None or data[0]=='':
                    #break
                    continue
                #elif self.cmd.CMD_BUZZER in data:
                #    if(data[1]=='1' or data[1]==1):
                #        self.control.order=data
                #        self.control.timeout=time.time()
                        #print("buzzer")
                        #self.control.L1=data[1]
                #    pass
                elif self.cmd.CMD_LED in data:
                    pass 
                elif self.cmd.CMD_LED_MOD in data:
                    pass
                elif self.cmd.CMD_HEAD in data:
                    pass
                elif self.cmd.CMD_SONIC in data:
                    pass
                elif self.cmd.CMD_POWER in data:
                    pass
                elif self.cmd.CMD_WORKING_TIME in data: 
                    pass
                else:
                    self.control.order=data
                    self.control.timeout=time.time()
                #print(data)
        try:    
            stop_thread(thread_led)
        except:
            pass
        try:    
            stop_thread(thread_sonic)
        except:
            pass
        print("stop control joystick_pub")
        stop_thread(self.control.Thread_conditiona)
        print("close_recv")
        #self.control.relax_flag=False
        #self.control.order[0]=self.cmd.CMD_RELAX
        

if __name__ == '__main__':
    pass
    
