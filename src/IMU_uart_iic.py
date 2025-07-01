import serial
import numpy as np
import time
import adafruit_bno055
import board
import busio

class IMU:
    def __init__(self, port, baudrate=500000):
#        self.serial_handle = serial.Serial(
#            port=port,
#            baudrate=baudrate,
#            parity=serial.PARITY_NONE,
#            stopbits=serial.STOPBITS_ONE,
#            bytesize=serial.EIGHTBITS,
#            timeout=0,
#        )
#        self.sensor = adafruit_bno055.BNO055_UART(self.serial_handle)  #uart，主板pin ,rx,tx串口读取，
        self.last_quat = np.array([1, 0, 0, 0])
        self.start_time = time.time()
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_bno055.BNO055_I2C(i2c)   #i2c读取
        #默认I2C硬件地址29， 库文件是读取28， 再/usr/local/lib/python3.7/dist-packages/adafruit_bno055.py， 第820行修改默认地址为29

    def flush_buffer(self):
         pass
#        self.serial_handle.reset_input_buffer()

    def read_orientation(self):
        """Reads quaternion measurements from the Teensy until none are left. Returns the last read quaternion.
        
        Parameters
        ----------
        serial_handle : Serial object
            Handle to the pyserial Serial object
        
        Returns
        -------
        np array (4,)
            If there was quaternion data to read on the serial port returns the quaternion as a numpy array, otherwise returns the last read quaternion.
        """

        while True:
            parsed = self.sensor.quaternion   #self.serial_handle.readline().decode("utf").strip()
            if parsed is "" or parsed is None:
                return self.last_quat
            else:
#                parsed = x.split(",")
#                if x != "":
                 self.last_quat = np.array(parsed, dtype=np.float64)
#                 print(self.last_quat)
#                else:
#                    print("Did not receive 4-vector from imu")
