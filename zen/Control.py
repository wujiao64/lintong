 # -*- coding: utf-8 -*-
import time
import math
import smbus
import copy
import threading
import numpy as np
from UDPComms import Publisher, Subscriber, timeout

class COMMAND:
    CMD_MOVE_STOP = "CMD_MOVE_STOP"
    CMD_MOVE_FORWARD = "CMD_MOVE_FORWARD" 
    CMD_MOVE_BACKWARD = "CMD_MOVE_BACKWARD"
    CMD_MOVE_LEFT = "CMD_MOVE_LEFT"
    CMD_MOVE_RIGHT = "CMD_MOVE_RIGHT"
    CMD_TURN_LEFT = "CMD_TURN_LEFT"
    CMD_TURN_RIGHT = "CMD_TURN_RIGHT"
    CMD_BUZZER = "CMD_BUZZER"
    CMD_LED_MOD = "CMD_LED_MOD"
    CMD_LED = "CMD_LED"
    CMD_BALANCE = "CMD_BALANCE"
    CMD_SONIC = "CMD_SONIC"
    CMD_HEIGHT = "CMD_HEIGHT"
    CMD_HORIZON = "CMD_HORIZON"
    CMD_HEAD = "CMD_HEAD"
    CMD_CALIBRATION = "CMD_CALIBRATION"
    CMD_POWER = "CMD_POWER"
    CMD_ATTITUDE = "CMD_ATTITUDE"
    CMD_RELAX = "CMD_RELAX"
    CMD_WORKING_TIME = "CMD_WORKING_TIME"
    def __init__(self):
        pass


class Control:
    def __init__(self):
        self.cmd=COMMAND()
        self.order = ['','','','','']
        self.relax_flag=True
        self.balance_flag=False
        self.attitude_flag=False
        self.Thread_conditiona=threading.Thread(target=self.condition)
        self.L1=0
        self.R1=0
        self.MESSAGE_RATE = 20
        self.msg = {
            "ly": 0, "lx": 0, "rx": 0, "ry": 0,
            "L2": 0, "R2": 0, "R1": 0, "L1": 0,
            "dpady": 0, "dpadx": 0,
            "x": 0,"square": 0,"circle": 0,"triangle": 0,
            "message_rate": self.MESSAGE_RATE,
        }

    def condition(self):
        ## Configurable ##
        self.joystick_pub = Publisher(8830)

        while True:
            if (self.order==['','','','','']):continue
            try:
                rx_ = 0
                ry_ = 0
                lx_ = 0
                ly_ = 0
                L1=0
                L2=0
                R1=0
                R2=0
                dpadx=0
                dpady=0
                x_button=0
                square=0
                circle=0
                triangle=0
                msg = {
                    "ly": 0, "lx": 0, "rx": 0, "ry": 0,
                    "L2": 0, "R2": 0, "R1": 0, "L1": 0,
                    "dpady": 0, "dpadx": 0,
                    "x": 0,"square": 0,"circle": 0,"triangle": 0,
                    "message_rate": self.MESSAGE_RATE,
                }
                if self.order[0] != '':
                    if self.order[0]==self.cmd.CMD_MOVE_STOP:
                        #self.stop()
                        continue #print("move=stop=")
                    elif self.order[0]==self.cmd.CMD_MOVE_FORWARD:
                        #self.forWard()
                        ly_=1  #0.5 #前进
                    elif self.order[0]==self.cmd.CMD_MOVE_BACKWARD:
                        #self.backWard()
                        ly_=-0.8 #-0.5 #后退
                    elif self.order[0]==self.cmd.CMD_MOVE_LEFT:
                        #self.setpLeft()
                        lx_=-1 #-0.5 #左踏步
                    elif self.order[0]==self.cmd.CMD_MOVE_RIGHT:
                        #self.setpRight()
                        lx_=1 #0.5 #右踏步
                    elif self.order[0]==self.cmd.CMD_TURN_LEFT:
                        #self.turnLeft()
                        rx_=-1 #-0.5    左转
                    elif self.order[0]==self.cmd.CMD_TURN_RIGHT:
                        #self.turnRight()
                        rx_=1 #0.5    右转
                    elif self.order[0]==self.cmd.CMD_RELAX:
                        R1=1
                        #print("R1=1,start")   踏步
                    elif self.order[0]==self.cmd.CMD_BUZZER:          # self.cmd.CMD_BUZZER in self.order:
                        if(self.order[1]=='1' or self.order[1]==1):
                            L1=1
                            #print("L1=1,start")   #待命
                        else:continue
                    elif self.order[0]==self.cmd.CMD_BALANCE: # and self.order[1]=='1':
                        continue
                    elif self.order[0]==self.cmd.CMD_HEIGHT:
                        continue#dpady=int(self.order[1])/200
                    elif self.order[0]==self.cmd.CMD_HORIZON:
                        continue
                    elif self.order[0]==self.cmd.CMD_ATTITUDE:
                        continue
                    elif self.order[0]==self.cmd.CMD_CALIBRATION:
                        continue

                    msg = {
                        "ly": ly_, "lx": lx_, "rx": rx_, "ry": ry_,
                        "L2": L2, "R2": R2, "R1": R1, "L1": L1,
                        "dpady": dpady, "dpadx": dpadx,
                        "x": x_button, "square": square, "circle": circle, "triangle": triangle,
                        "message_rate": self.MESSAGE_RATE,
                    }
                    if(L1==1) or (R1==1):
                        R1=0
                        L1=0
                        self.order=['','','','','']

                    self.joystick_pub.send(msg)
                    #print(msg)
                    time.sleep(0.01)

            except Exception as e:
                print("joystick pub error",e)


if __name__=='__main__':
    pass

