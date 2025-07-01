import numpy as np
import time
from src.IMU import IMU
from src.Controller import Controller
from src.JoystickInterface import JoystickInterface
from src.State import State
#import src.joystick2.4g
from pupper.HardwareInterface import HardwareInterface
from pupper.Config import Configuration
from pupper.Kinematics import four_legs_inverse_kinematics

import fcntl
import struct
import socket
#import picamera
#import threading
from src.Led import *

#import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from multiprocessing import Process
import multiprocessing
from IMU.IMU import IMU




class robot:
    def __init__(self):
        self.quat_orientation = np.array([1, 0, 0, 0])  # IMU orientation data (Quaternions)
#        self.led=Led()
        #ip adress
#        HOST=self.get_interface_ip()
#        print(HOST)
#        #Port 8000 for video transmission
#        self.server_socket = socket.socket()
#        self.server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
#        self.server_socket.bind((HOST, 8001))              
#        self.server_socket.listen(1)

#        self.video=threading.Thread(target=self.transmission_video)
#        self.video.start()

        # Raspberry Pi pin configuration:
        RST = None     # on the PiOLED this pin isnt used
        # Note you can change the I2C address by passing an i2c_address parameter like:
        #disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)
        # 128x32 display with hardware I2C:
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_address=0x3C)
        # Initialize library.
        self.disp.begin()
        # Clear display.
        self.disp.clear()
        self.disp.display()
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new('1', (self.width, self.height))
        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)
        # Draw some shapes.
        # First define some constants to allow easy resizing of shapes.
        padding = -2
        self.top = padding
        bottom = self.height-padding
        # Move left to right keeping track of the current x position for drawing shapes.
        self.x = 0
        # Load default font.
        self.font = ImageFont.load_default()
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)
        self.draw.text((self.x, self.top), u"robot dog start...",  font=self.font, fill=255)
#        self.draw.text((self.x, self.top+8), "IP: " + HOST,  font=self.font, fill=255)
        # Display image.
        self.disp.image(self.image)
        self.disp.display()


    def Oled_show(self,oled_text=""):
        #disp.clear()
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)
        # Write two lines of text.
        #top=top+8
        self.draw.text((self.x, self.top), str(oled_text),  font=self.font, fill=255)
        # Display image.
        self.disp.image(self.image)
        self.disp.display()



    def get_interface_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                                            0x8915,
                                            struct.pack('256s',b'wlan0'[:15])
                                            )[20:24])

    def IMU_read(self, use_IMU, imu):
        """IMU data read program
        """
        global quat_orientation
        if use_IMU:
            while True:
                self.quat_orientation = imu.read_orientation()
                print(self.quat_orientation)
                time.sleep(0.01)
                #time.sleep(poll_interval*1.0/1000.0)
        else:
            self.quat_orientation = np.array([1, 0, 0, 0])


    def dogbot(self,use_imu=False):
        """Main program
        """
        led=Led()
        #Red wipe
        led.colorWipe(led.strip, Color(55, 0, 0))
        #time.sleep(12)
        #Oled_show("robot start...")
        # Create config
        config = Configuration()
        hardware_interface = HardwareInterface()

        use_IMU = True
        # sleep 5s to wait for booting up complete
        time.sleep(2.0)
        # Create imu handle
        if use_IMU:
            imu = IMU()
            time.sleep(0.1)
            imu.begin()
            time.sleep(0.1)
            # Startup the IMU data reading thread
            try:
                _imuThread = threading.Thread(target=IMU_read, args=(use_IMU, imu,))
                _imuThread.start()
            except:
                print("Error: IMU thread could not startup!!!")

        # Create controller and user input handles
        controller = Controller(
            config,
            four_legs_inverse_kinematics,
        )
        state = State()
        print("Creating joystick listener...")
        self.Oled_show("Creating joystick listener...")
        joystick_interface = JoystickInterface(config)
        print("Done.")
        #White wipe
        led.colorWipe(led.strip, Color(55, 55, 55))

        last_loop = time.time()

        print("Summary of gait parameters:")
        print("overlap time: ", config.overlap_time)
        print("swing time: ", config.swing_time)
        print("z clearance: ", config.z_clearance)
        print("x shift: ", config.x_shift)

        # Wait until the activate button has been pressed
        while True:
            #Blue wipe
            print ("\nBlue wipe")
            led.colorWipe(led.strip, Color(0, 0, 55)) 
            print("Waiting for L1 to activate robot.")
            self.Oled_show("Waiting for L1 to activate robot.")
            while True:
                command = joystick_interface.get_command(state)
                joystick_interface.set_color(config.ps4_deactivated_color)
                if command.activate_event == 1:
                    break
                time.sleep(0.1)
            #Green wipe
            led.colorWipe(led.strip, Color(0, 55, 0)) 
            print("Robot activated.")
            self.Oled_show("Robot activated.")

            joystick_interface.set_color(config.ps4_color)

            while True:
                now = time.time()
                if now - last_loop < config.dt:
                    continue
                last_loop = time.time()

                # Parse the udp joystick commands and then update the robot controller's parameters
                command = joystick_interface.get_command(state)
                if command.activate_event == 1:
                    print("Deactivating Robot")
                    self.Oled_show("Deactivating Robot.")
                    #Blue wipe
                    led.colorWipe(led.strip, Color(0, 0, 55)) 
                    break

                # Read imu data. Orientation will be None if no data was available
                #quat_orientation = (
                #    imu.read_orientation() if use_imu else np.array([1, 0, 0, 0])
                #)
                state.quat_orientation = self.quat_orientation

                # Step the controller forward by dt
                controller.run(state, command)

                # Update the pwm widths going to the servos
                hardware_interface.set_actuator_postions(state.joint_angles)


#if __name__ == '__main__':
    #time.sleep(10)
rbt=robot()
rbt.dogbot()
