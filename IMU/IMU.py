import board
import busio
import numpy as np
import time
import RPi.GPIO as GPIO

import sys, getopt

sys.path.append('.')
import RTIMU
import os.path
import time
import math


#  computeHeight() - the conversion uses the formula:
#
#  h = (T0 / L0) * ((p / P0)**(-(R* * L0) / (g0 * M)) - 1)
#
#  where:
#  h  = height above sea level
#  T0 = standard temperature at sea level = 288.15
#  L0 = standard temperatur elapse rate = -0.0065
#  p  = measured pressure
#  P0 = static pressure = 1013.25
#  g0 = gravitational acceleration = 9.80665
#  M  = mloecular mass of earth's air = 0.0289644
#  R* = universal gas constant = 8.31432
#
#  Given the constants, this works out to:
#
#  h = 44330.8 * (1 - (p / P0)**0.190263)

def computeHeight(pressure):
    return 44330.8 * (1 - pow(pressure / 1013.25, 0.190263));
    
    

def filter_deabnormal(data_new,data_last):
    ''' deabnormal filter, remove the abnormal value.

		Parameter:
		data_new : the new IMU data
		data_last: the last IMU data

		Return:
		data_normal: the IMU data that have remove abnormal value
	'''
    data_normal = data_new
    for index in range(4):
        if abs(data_new[index] - data_last[index])>1:
            data_normal[index] = data_last[index]
    return data_normal

def filter_lowpass(data_new,data_last):
    ''' low pass filter.

		Parameter:
		data_new : the new IMU data
		data_last: the last IMU data

		Return:
		data_lowpass: the low frequencey IMU data
	'''
    data_lowpass = data_new

    for index in range(4):
        data_lowpass[index] = data_last[index]*0.8 + data_new[index]*0.2
    return data_lowpass

class IMU:
    def __init__(self):
        self.last_quat = [1, 0, 0, 0]
        self.reset_IMU = False

    def begin(self):
        print("")

 
    def read_orientation(self):
        """Reads quaternion measurements from the Teensy . Returns the read quaternion.
                np array (4,)
                    If there was quaternion data to read on the I2C port returns the quaternion as a numpy array, otherwise returns the last read quaternion.
        """
        SETTINGS_FILE = "RTIMULib"
        print("Using settings file " + SETTINGS_FILE + ".ini")
        if not os.path.exists(SETTINGS_FILE + ".ini"):
          print("Settings file does not exist, will be created")
        s = RTIMU.Settings(SETTINGS_FILE)
        self.imu = RTIMU.RTIMU(s)
        self.pressure = RTIMU.RTPressure(s)
        print("IMU Name: " + self.imu.IMUName())
        print("Pressure Name: " + self.pressure.pressureName())
        if (not self.imu.IMUInit()):
            print("IMU Init Failed")
            sys.exit(1)
        else:
            print("IMU Init Succeeded");
        # this is a good time to set any fusion parameters

        self.imu.setSlerpPower(0.02)
        self.imu.setGyroEnable(True)
        self.imu.setAccelEnable(True)
        self.imu.setCompassEnable(True)
        if (not self.pressure.pressureInit()):
            print("Pressure sensor Init Failed")
        else:
            print("Pressure sensor Init Succeeded")
        self.poll_interval = self.imu.IMUGetPollInterval()
        #print("Recommended Poll Interval: %dmS\n" % self.poll_interval)
        
        try:
            #while True:
                    if self.imu.IMURead():
                        # x, y, z = imu.getFusionData()
                        # print("%f %f %f" % (x,y,z))
                        data = self.imu.getIMUData()
                        (data["fusionQposeValid"]) = self.pressure.pressureRead()
                        #(data["pressureValid"], data["pressure"], data["temperatureValid"], data["temperature"]) = pressure.pressureRead()
                        #print(data["fusionQPose"])
                        fusionPose = data["fusionQPose"]
                        #print("[ %f , %f , %f, %f ]" % (math.degrees(fusionPose[0]), math.degrees(fusionPose[1]), math.degrees(fusionPose[2]), math.degrees(fusionPose[3])))
                        #quat_i, quat_j, quat_k, quat_real = self.imu.quaternion
                        #quat_orientation = [quat_real, quat_i, quat_j, quat_k]
                        quat_orientation = [math.degrees(fusionPose[0]), math.degrees(fusionPose[1]), math.degrees(fusionPose[2]), math.degrees(fusionPose[3])]
                        new_quat = np.array(quat_orientation, dtype=np.float64)
                        normal_quat = filter_deabnormal(new_quat, self.last_quat)
                        lp_quat = filter_lowpass(normal_quat, self.last_quat)
                        #self.last_quat = lp_quat
                        #time.sleep(poll_interval*1.0/1000.0)
                        self.last_quat = quat_orientation
                        return self.last_quat
        except:
            #GPIO.output(self.imu_resetIO, 0)
            self.reset_IMU = True
            time.sleep(0.05)
            return self.last_quat



def IMU_read(use_IMU, imu):
    """IMU data read program
    """
    global quat_orientation
    if use_IMU:
        while True:
            quat_orientation = imu.read_orientation()
            print(quat_orientation)
            time.sleep(0.01)
            #time.sleep(poll_interval*1.0/1000.0)
    else:
        quat_orientation = np.array([1, 0, 0, 0])

def main():
    use_IMU=True
    imu = IMU()
    time.sleep(0.1)
    imu.begin()
    time.sleep(0.1)
    # Startup the IMU data reading thread
    IMU_read(use_IMU, imu) 
    
if __name__=="__main__":
    #main()
    pass
