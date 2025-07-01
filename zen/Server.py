# -*- coding: utf-8 -*-
import io
import os
import time
import fcntl
import socket
import struct
import picamera
import threading
from zen.Thread import *
from zen.Control import *


class Server:
    def __init__(self):
        self.tcp_flag=False
        self.control=Control()
        self.cmd=COMMAND()
        self.battery_voltage=[8.4,8.4,8.4,8.4,8.4]

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
            print("conn wifi:",ifname)
            return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', bytes(ifname[:15],'utf-8'))     #python3
                #struct.pack('256s', ifname[:15])                   #python2
                )[20:24])
        except Exception as e:
            print(e)

            try:
                ifname="wlan1"
                print("conn wifi:",ifname)
                return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                    0x8915,  # SIOCGIFADDR
                    struct.pack('256s', bytes(ifname[:15],'utf-8'))     #python3
                    #struct.pack('256s', ifname[:15])                   #python2
                    )[20:24])
            except Exception as e:
                print(e)
                return 0

    def turn_on_server(self):
        #ip adress
        #HOST=self.get_interface_ip('wlan0')
        HOST=0
        while (HOST==0): #True:
            #ip adress
            HOST=self.get_interface_ip('wlan0')
            if (HOST==0):time.sleep(5)

        #Port 8000 for video transmission
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
        self.server_socket.bind((HOST, 8001))              
        self.server_socket.listen(1)
        
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
            #self.server_socket.close()
            #self.server_socket1.close()
            #stop_thread(self.control.Thread_conditiona)
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
            self.connection=self.connection.makefile('wb')
        except:
            pass
        self.server_socket.close()
        try:
            with picamera.PiCamera() as camera:
                camera.resolution = (400,300)       # pi camera resolution
                camera.framerate = 15               # 15 frames/sec
                camera.saturation = 80              # Set image video saturation
                camera.brightness = 50              # Set the brightness of the image (50 indicates the state of white balance)
                camera.rotation = 180                 #是否对图像进行旋转 
                start = time.time()
                stream = io.BytesIO()
                # send jpeg format video stream
                print ("Start transmit ... ")
                for foo in camera.capture_continuous(stream, 'jpeg', use_video_port = True):
                    try:
                        self.connection.flush()
                        stream.seek(0)
                        b = stream.read()
                        lengthBin = struct.pack('L', len(b))
                        self.connection.write(lengthBin)
                        self.connection.write(b)
                        stream.seek(0)
                        stream.truncate()
                    except BaseException as e:
                        #print (e)
                        print ("End transmit ... " )
                        #camera.release()
                        self.reset_server()
                        #return
                        #continue
                        break
        except BaseException as e:
            print(e)
            print ("Camera unintall")

    def sednRelaxFlag(self):
        if self.control.move_flag!=2:
            command=self.cmd.CMD_RELAX+"#"+str(self.control.move_flag)+"\n"
            self.send_data(self.connection1,command)
            self.control.move_flag= 2  
                  
    def receive_instruction(self):
        try:
            self.connection1,self.client_address1 = self.server_socket1.accept()
            print ("Client connection successful !")

            self.control.Thread_conditiona.start()
            print ("control joystick_pub start...")

        except:
            print ("Client connect failed")
        self.server_socket1.close()
        while True:
            try:
                allData=self.connection1.recv(1024).decode('utf-8')
                #print(allData)
            except:
                if self.tcp_flag:
                    #if max(self.battery_voltage) > 6.4:
                    #    self.reset_server()
                    self.reset_server()
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
                    continue
                #elif self.cmd.CMD_BUZZER in data:
                #    print("buzzer")
                #    self.control.L1=1
                #    pass
                elif self.cmd.CMD_LED in data:
                    continue
                elif self.cmd.CMD_LED_MOD in data:
                    continue
                elif self.cmd.CMD_HEAD in data:
                    continue
                elif self.cmd.CMD_SONIC in data:
                    continue
                elif self.cmd.CMD_POWER in data:
                    continue
                elif self.cmd.CMD_WORKING_TIME in data: 
                    continue
                else:
                    self.control.order=data
                    self.control.timeout=time.time()

        try:    
            stop_thread(thread_power)
        except:
            pass
        try:    
            stop_thread(thread_led)
        except:
            pass
        print("stop control joystick_pub")
        #stop_thread(self.control.Thread_conditiona)
        print("close_recv")
        #self.control.relax_flag=False
        #self.control.order[0]=self.cmd.CMD_RELAX
        

if __name__ == '__main__':
    pass
    
