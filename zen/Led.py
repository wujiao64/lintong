# -*-coding: utf-8 -*-
import time
from rpi_ws281x import *
# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
# Define functions which animate LEDs in various ways.
class Led:
    def __init__(self):
        self.LedMod='1'
        self.colour=[0,0,0]
        #Control the sending order of color data
        self.ORDER = "RGB"  
        # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()
    def LED_TYPR(self,order,R_G_B):
        B=R_G_B & 255
        G=R_G_B >> 8 & 255
        R=R_G_B >> 16 & 255 
        Led_type=["GRB","GBR","RGB", "RBG","BRG","BGR"]
        color = [Color(G,R,B),Color(G,B,R),Color(R,G,B),Color(R,B,G),Color(B,R,G),Color(B,G,R)]
        if order in Led_type:
            return color[Led_type.index(order)]
    def colorWipe(self,strip, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        color=self.LED_TYPR(self.ORDER,color)
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def colorChange(self,r=0,g=0,b=0):
        self.colorWipe(self.strip, Color(r, g, b))

    def theaterChase(self,strip, color, wait_ms=50, iterations=10):
        """Movie theater light style chaser animation."""
        color=self.LED_TYPR(self.ORDER,color)
        for j in range(iterations):
            for q in range(3):
                for i in range(0,self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, color)
                self.strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, 0)

    def wheel(self,pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos<0 or pos >255:
            r=g=b=0
        elif pos < 85:
            r=pos * 3
            g=255 - pos * 3
            b=0
        elif pos < 170:
            pos -= 85
            r=255 - pos * 3
            g=0
            b=pos * 3
        else:
            pos -= 170
            r=0
            g=pos * 3
            b=255 - pos * 3
        return self.LED_TYPR(self.ORDER,Color(r,g,b))

    def rainbow(self,strip, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256*iterations):
            for i in range(self.strip.numPixels()):
                 self.strip.setPixelColor(i, self.wheel((i+j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def rainbowCycle(self,strip, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256*iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel((int(i * 256 / self.strip.numPixels()) + j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def theaterChase(self,strip,data, wait_ms=50):
        for q in range(3):
            for i in range(0, self.strip.numPixels(), 3):
                self.strip.setPixelColor(i+q,Color(data[0],data[1],data[2]))
            self.strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)
    def ledIndex(self,index,R,G,B):
        color=self.LED_TYPR(self.ORDER,Color(R,G,B))
        for i in range(8):
            if index & 0x01 == 1:
                self.strip.setPixelColor(i,color)
            index=index >> 1
        self.strip.show()
    def light(self,data):
        oldMod=self.LedMod
        if len(data) <5:
            self.LedMod=data[1]
        else:
            for i in range(3):
                self.colour[i]=int(data[i+2])
        if self.LedMod=='0':
            self.colorWipe(self.strip, Color(0,0,0))
            self.LedMod=oldMod
        elif self.LedMod=='1':
            self.ledIndex(255,self.colour[0],self.colour[1],self.colour[2])
        elif self.LedMod=='2':
            while True:
                self.colorWipe(self.strip, Color(255, 0, 0))   #Red wipe
                self.colorWipe(self.strip, Color(0, 255, 0))   #Green wipe
                self.colorWipe(self.strip, Color(0, 0, 255))   #Blue wipe
        elif self.LedMod=='3':
            while True:
                self.theaterChase(self.strip,self.colour)
        elif self.LedMod=='4':
            while True:
                self.rainbow(self.strip)
        elif self.LedMod=='5':
            while True:
                self.rainbowCycle(self.strip)

# Main program logic follows:
if __name__ == '__main__':
    pass
        
