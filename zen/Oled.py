#import os
#import sys
#import threadingsys.path.append("..")
#sys.path.extend([os.path.join(root, name) for root, dirs, _ in os.walk("../") for name in dirs])

import fcntl
import struct
import socket

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

#import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306


class Oled:
    def __init__(self):
        #ip adress
#        HOST=self.get_interface_ip('wlan0')    #self.get_host_ip()    #
#        print(HOST)

        # Raspberry Pi pin configuration:
        RST = None     # on the PiOLED this pin isnt used
        # Note you can change the I2C address by passing an i2c_address parameter like:
        #disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)
        # 128x32 display with hardware I2C:
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=1, i2c_address=0x3C)  #1,raspberry 
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
        # Draw a black filled box to clear the image.  黑屏
        self.draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)

#        self.draw.text((self.x, self.top), u"robot dog start...",  font=self.font, fill=255)
#        self.draw.text((self.x, self.top+12), "IP: " + HOST,  font=self.font, fill=255)

        # Display image.
        self.disp.image(self.image)
        self.disp.display()


    def show_text(self,oled_text=""):
        #ip adress
        HOST=self.get_interface_ip('wlan0')
        #disp.clear()
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)
        # Write two lines of text.
        #top=top+8
        self.draw.text((self.x, self.top), str(oled_text),  font=self.font, fill=255)
        self.draw.text((self.x, self.top+12), "IP: " + HOST,  font=self.font, fill=255)
        # Display image.
        self.disp.image(self.image)
        self.disp.display()


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
#if __name__ == '__main__':
    #time.sleep(10)
#oled=Oled()
#oled.Oled_show()
