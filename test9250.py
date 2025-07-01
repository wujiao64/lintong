import os
import sys
import threading
import time

import numpy as np

from multiprocessing import Process
import multiprocessing
from IMU.IMU import IMU

quat_orientation = np.array([1, 0, 0, 0])  # IMU orientation data (Quaternions)

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
    """Main program
    """
    use_IMU = True

    # sleep 5s to wait for booting up complete
    time.sleep(5.0)

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

    last_loop = time.time()
    while True:
        print("Waiting for L1 to activate robot.")
        while True:
            now = time.time()
            if now - last_loop < 0.015: #config.dt:
                continue
            last_loop = time.time()

            # Read imu data. Orientation will be None if no data was available
            #state.quat_orientation = quat_orientation

try:
    main()
except KeyboardInterrupt:
    pass
