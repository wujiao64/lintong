import numpy as np
import time
#from src.JoystickPS4 import JoystickPS4
#from src.Joystick24g import Joystick24g
from zen.Server import *

import fcntl
import struct
import socket
import picamera
import threading

class robot_video:
    def __init__(self):
        self.server=Server()

    def get_host_ip(self):
        try:
            s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            s.connect(('8.8.8.8',80))
            ip = s.getsockname()[0]
        except Exception as e:
            print(e)
            return "no wifi"
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

    def joystick_swicth(self):
        event="NO"   #  "PS4"  ,  "24G"   ,  "NO"
        if event=="24G":
            joystick=Joystick24g('/dev/input/by-id/usb-MY-POWER_LeWGP-201-event-joystick')
            joystick.GetCMD()
            print("use LETV 2.4G JOYSTICK")
        elif event=="PS4":
            joystick=JoystickPS4("PS4")
            joystick.GetCMD()
            print("use PS4 JOYSTICK")

        return

    def on_server(self):
            self.server.turn_on_server()
            self.server.tcp_flag=True
            self.video=threading.Thread(target=self.server.transmission_video)
            self.video.start()
            self.instruction=threading.Thread(target=self.server.receive_instruction)
            self.instruction.start()

            self.joy=threading.Thread(target=self.joystick_swicth)  #如果需要遥控手柄控制，请去掉前面2行注释
            self.joy.start()                                     #如果需要遥控手柄控制，请去掉前面2行注释

    def off_server(self):
            self.server.tcp_flag=False
            try:
                stop_thread(self.video)
                stop_thread(self.instruction)
            except Exception as e:
                print(e)
            self.server.turn_off_server()
            print("close")
    def closeEvent(self,event):
        try:
            stop_thread(self.video)
            stop_thread(self.instruction)
            stop_thread(self.joy)                             #如果需要遥控手柄控制，请去掉前面行注释
        except:
            pass
        try:
            self.server.server_socket.shutdown(2)
            self.server.server_socket1.shutdown(2)
            self.server.turn_off_server()
        except:
            pass
        os._exit(0)

#if __name__ == '__main__':
time.sleep(10) #如果是局域网固定IP，可以注释掉此行， 此延时10秒钟只准对wifi自动获取IP地址需要。
rbt=robot_video()
rbt.on_server()

