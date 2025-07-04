from UDPComms import Publisher, Subscriber, timeout
from PS4Joystick import Joystick

import time

## you need to git clone the PS4Joystick repo and run `sudo bash install.sh`

####################################################################################    
######################______JOYSTICK FUNCTION_______################################
####################################################################################  
class JoystickPS4():
    def __init__(self , event):
    ## Configurable ##
        self.MESSAGE_RATE = 20
        self.PUPPER_COLOR = {"red":0, "blue":0, "green":255}

        self.joystick_pub = Publisher(8830)
        self.joystick_subcriber = Subscriber(8840, timeout=0.01)
        self.joystick = Joystick()
        self.joystick.led_color(**self.PUPPER_COLOR)


    def GetCMD(self):
        while True:
            #print("running")
            values = self.joystick.get_input()

            left_y = -values["left_analog_y"]
            right_y = -values["right_analog_y"]
            right_x = values["right_analog_x"]
            left_x = values["left_analog_x"]

            L2 = values["l2_analog"]
            R2 = values["r2_analog"]

            R1 = values["button_r1"]
            L1 = values["button_l1"]

            square = values["button_square"]
            x = values["button_cross"]
            circle = values["button_circle"]
            triangle = values["button_triangle"]

            dpadx = values["dpad_right"] - values["dpad_left"]
            dpady = values["dpad_up"] - values["dpad_down"]

            msg = {
                "ly": left_y,
                "lx": left_x,
                "rx": right_x,
                "ry": right_y,
                "L2": L2, "R2": R2,
                "R1": R1, "L1": L1,
                "dpady": dpady,"dpadx": dpadx, "x": x,
                "square": square, "circle": circle, "triangle": triangle,
                "message_rate": self.MESSAGE_RATE,
            }
            self.joystick_pub.send(msg)

            try:
                msg = self.joystick_subcriber.get()
                self.joystick.led_color(**msg["ps4_color"])
            except timeout:
                pass

            time.sleep(1 / self.MESSAGE_RATE)


############################################################################
#######################______main()_______##################################
############################################################################            
def main():
    joystick=JoystickPS4("PS4")
    joystick.GetCMD()

if __name__== "__main__":
    #main()
    pass
