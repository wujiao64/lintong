from UDPComms import Publisher, Subscriber, timeout
#import pygame
import numpy
import math
import time
from evdev import InputDevice, categorize, ecodes
from select import select



####################################################################################    
######################______JOYSTICK FUNCTION_______################################
####################################################################################  
class Joystick24g():
    def __init__(self , event):
        self.gamepad = InputDevice(event)    #('/dev/input/by-id/usb-MY-POWER_LeWGP-201-event-joystick')
        self.d_x=0.
        self.d_y=0.
        self.d_z=0.
        self.d_rx=0.
        self.d_ry=0.
        self.d_pitch=0.
        self.d_yaw=0.
        self.d_roll=0.
        self.MESSAGE_RATE = 20
        self.msg = {
            "ly": 0, "lx": 0, "rx": 0, "ry": 0,
            "L2": 0, "R2": 0, "R1": 0, "L1": 0,
            "dpady": 0, "dpadx": 0,
            "x": 0,"square": 0,"circle": 0,"triangle": 0,
            "message_rate": self.MESSAGE_RATE,
        }
        ## Configurable ##
        #self.PUPPER_COLOR = {"red":0, "blue":0, "green":255}
        self.joystick_pub = Publisher(8830)
        #joystick_subcriber = Subscriber(8840, timeout=0.01)

    @staticmethod
    def map(val, in_min, in_max, out_min, out_max):
        """ helper static method that helps with rescaling """
        in_span = in_max - in_min
        out_span = out_max - out_min

        value_scaled = float(val - in_min) / float(in_span)
        value_mapped = (value_scaled * out_span) + out_min

        if value_mapped < out_min:
            value_mapped = out_min

        if value_mapped > out_max:
            value_mapped = out_max

        return value_mapped

    def deadzones(self):
        deadzone = 0.14
        if math.sqrt( self.d_x ** 2  + self.d_y ** 2) < deadzone:
            self.d_x = 0.
            self.d_y = 0.
        if math.sqrt( self.d_rx ** 2  + self.d_ry ** 2) < deadzone:
            self.d_rx = 0.
            self.d_ry = 0.
        return True

    def Read(self):
        #print(self.gamepad.get_power_level)
        r,w,x = select([self.gamepad.fd], [], [], 0.1)
        #d_x=0
        #d_y=0
        #d_rx=0
        #d_ry=0
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
        if r:
            for event in self.gamepad.read():
                #print(event)
                #print("type:")
                #print(event.type)
                #print(",code:")
                #print(event.code)
                #print("val:")
                #print(event.value)
                if event.type == ecodes.EV_KEY:
                    if event.value == 1:
                        if event.code == 288:
                            print(d_y)
                        if event.code == 289:
                            print(d_y)
                    else:
                        if event.code==310:
                            print("L1=LB")
                            L1=1
                        if event.code==311:
                            print("R1=RB")
                            R1=1
                        if event.code==308:
                            print("triangle : Y")
                            triangle=1
                        if event.code==304:
                            print("cross : A")
                            x_button=1
                        if event.code==307:
                            print("square : X")
                            square=1
                        if event.code==305:
                            print("circle : B")
                            circle=1
                        if event.code==315:
                            print("start ")
                        #print("boton soltado")
                ########################################  for my own joystick
                #      ^           #     ^            #
                #    ABS_Y         #    ABS_RY        #
                #  ←─────→ ABS_X   #  ←─────→ ABS_RX  #
                #     ↓            #     ↓            #  
                #######################################
                elif event.type == ecodes.EV_ABS:
                    absevent = categorize(event)
                    if ecodes.bytype[absevent.event.type][absevent.event.code] == "ABS_X":  
                        self.d_x=(absevent.event.value-127)/128.
                    elif ecodes.bytype[absevent.event.type][absevent.event.code] == "ABS_Y":
                        self.d_y=-(absevent.event.value-127)/128.
                    elif ecodes.bytype[absevent.event.type][absevent.event.code] == "ABS_RZ":
                        self.d_ry=-(absevent.event.value-127)/128.
                    elif ecodes.bytype[absevent.event.type][absevent.event.code] == "ABS_Z":
                        self.d_rx=(absevent.event.value-127)/128.
                    if event.code == 17:
                        dpady=-event.value
                        if event.value ==-1:
                            print("dpady:up=-1")
                        if event.value ==1:
                            print("dpady:down=1")
                    if event.code == 16:
                        dpadx=-event.value
                        if event.value ==-1:
                            print("dpadx:left=-1")
                        if event.value ==1:
                            print("dpadx:right=1")
        self.deadzones()

        msg = {
                    "ly": self.d_y, "lx": self.d_x, 
                    "rx": self.d_rx, "ry": self.d_ry,
                    "L2": L2, "R2": R2, "R1": R1, "L1": L1,
                    "dpady": dpady, "dpadx": dpadx,
                    "x": x_button, "square": square, "circle": circle, "triangle": triangle,
                    "message_rate": self.MESSAGE_RATE,
                }
        self.joystick_pub.send(msg)
        #print(msg)
        return self.d_x , self.d_y , self.d_rx , self.d_ry


    def GetCMD(self):
        while(True):
            d_y , d_x , d_rx , d_ry = self.Read()
    #        print(d_x,d_y,d_z)
    #        d_yaw, d_pitch = PID.rotacion(yaw , pitch) 
    #        print(yaw , pitch)
    #        d_x= -1 + yaw/compensateXZ
    #        d_z= -pitch/compensateXZ
        #time.sleep(1 / MESSAGE_RATE)
            time.sleep(0.02)


############################################################################
#######################______main()_______##################################
############################################################################            
def main():
    #initialize all the classes
#    PID=PIDcontrol()    
    joystick=Joystick24g('/dev/input/by-id/usb-MY-POWER_LeWGP-201-event-joystick')
    joystick.GetCMD()

        
        
if __name__== "__main__":
#    main()
    pass
