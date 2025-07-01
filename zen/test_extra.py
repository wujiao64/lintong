import time
from Led import *
led=Led()
def test_Led():
    try:
        #Red wipe
        print ("\nRed wipe")
        led.colorChange(255, 0, 0) 
        time.sleep(1)
        
        
        #Green wipe
        print ("\nGreen wipe")
        led.colorChange(0, 255, 0) 
        time.sleep(1)
        
        
        #Blue wipe
        print ("\nBlue wipe")
        led.colorChange(0, 0, 255)
        time.sleep(1)
        
        
        #White wipe
        print ("\nWhite wipe")
        led.colorChange(255, 255, 255)
        time.sleep(1)
        
        led.colorChange(0, 0, 0)   #turn off the light
        print ("\nEnd of program")
    except KeyboardInterrupt:
        led.colorChange(0, 0, 0)   #turn off the light
        print ("\nEnd of program")

from Ultrasonic import *
ultrasonic=Ultrasonic()                
def test_Ultrasonic():
    try:
        while True:
            data=ultrasonic.getDistance()   #Get the value
            print ("Obstacle distance is "+str(data)+"CM")
            time.sleep(1)
    except KeyboardInterrupt:
        print ("\nEnd of program")


from Buzzer import *
buzzer=Buzzer()
def test_Buzzer():
    try:
        buzzer.run('1')
        time.sleep(1)
        print ("1S")
        time.sleep(1)
        print ("2S")
        time.sleep(1)
        print ("3S")
        buzzer.run('0')
        print ("\nEnd of program")
    except KeyboardInterrupt:
        buzzer.run('0')
        print ("\nEnd of program")
     
# Main program logic follows:
if __name__ == '__main__':

    print ('Program is starting ... ')
    import sys
    if len(sys.argv)<2:
        print ("Parameter error: Please assign the device")
        exit() 
    if sys.argv[1] == 'Led':
        test_Led()
    elif sys.argv[1] == 'Ultrasonic':
        test_Ultrasonic()
    elif sys.argv[1] == 'Buzzer':   
        test_Buzzer() 


