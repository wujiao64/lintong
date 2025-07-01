import time
import board
import busio
import numpy as np
#import serial
import RPi.GPIO as GPIO
import adafruit_bno055

#imu_resetIO = 22
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(imu_resetIO, GPIO.OUT)
#GPIO.output(imu_resetIO, 1)
#time.sleep(0.1)
#GPIO.output(imu_resetIO, 0)
#time.sleep(0.1)

#uart = serial.Serial("/dev/serial0")
#sensor = adafruit_bno055.BNO055_UART(uart)
i2c = busio.I2C(board.SCL, board.SDA)
#i2c = board.I2C()
sensor = adafruit_bno055.BNO055_I2C(i2c) 
time.sleep(0.1)
reset_IMU = False
last_quat=[1, 0, 0, 0]

last_val = 0xFFFF

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


#    print("去除嵌套括号后为:"+removeNestedPare(strs))
def removeNestedPare(strs):
    if strs == None:
        return strs
    Parentheses_num = 0  # 用来记录不匹配的"("出现的次数
    if list(strs)[0] != '(' or list(strs)[-1] != ')':
        return None
 
    sb = ''
    # 字符串首尾的括号可以单独处理
    i = 1
    while i < len(strs) - 1:
        ch = list(strs)[i]
        if ch == '(':
            Parentheses_num += 1
        elif ch == ')':
            Parentheses_num -= 1
        else:
            sb = sb + (list(strs)[i])
        i += 1
 
    # 判断括号是否匹配
    if Parentheses_num != 0:
        print("由于括号不匹配，因此不做任何操作")
        return None
    # 处理字符串结尾的')'
    sb = sb + ''
    return sb


def temperature():
    global last_val  # pylint: disable=global-statement
    result = sensor.temperature
    if abs(result - last_val) == 128:
        result = sensor.temperature
        if abs(result - last_val) == 128:
            return 0b00111111 & result
    last_val = result
    return result 



while True:
#    print("Temperature: {} degrees C".format(sensor.temperature))
    print("Temperature: {} degrees C".format(temperature()))  # Uncomment if using a Raspberry Pi
    print("Accelerometer (m/s^2): {}".format(sensor.acceleration))
    print("Magnetometer (microteslas): {}".format(sensor.magnetic))
    print("Gyroscope (rad/sec): {}".format(sensor.gyro))
    print("Euler angle: {}".format(sensor.euler))
    print("Quaternion: {}".format(sensor.quaternion))
    print("Linear acceleration (m/s^2): {}".format(sensor.linear_acceleration))
    print("Gravity (m/s^2): {}".format(sensor.gravity))
    print()
    print("---------------------------------------")
    
#    print("Euler angle: {}".format(sensor.euler) +",Quaternion: {}".format(sensor.quaternion))
#    print("{}".format(sensor.quaternion))
#    x=sensor.quaternion
#    x=removeNestedPare(sensor.quaternion)
    """
    quat_i, quat_j, quat_k, quat_real = sensor.quaternion	#self.imu.quaternion
    quat_orientation = [quat_real, quat_i, quat_j, quat_k]
    new_quat = np.array(quat_orientation, dtype=np.float64)
    normal_quat = filter_deabnormal(new_quat, last_quat)
    lp_quat = filter_lowpass(normal_quat, last_quat)
    last_quat = lp_quat
    #return self.last_quat
    print(last_quat)
    """
    time.sleep(1)

