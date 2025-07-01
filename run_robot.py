
from zen.Led import *
from zen.Oled import *

import numpy as np
import time
from src.IMU import IMU
from src.Controller import Controller
from src.JoystickInterface import JoystickInterface
from src.State import State

from pupper.HardwareInterface import HardwareInterface
from pupper.Config import Configuration
from pupper.Kinematics import four_legs_inverse_kinematics

class robot:
    def __init__(self):
        print("robot dog init.")

    def cmd_dump(self,cmd):
        """
           debug interface to show all info about PS4 command
           Parameter: None
           return : None
        """
        print("\nGet JOYSTICK command :-------------------------")
#        print("horizontal_velocity: ", cmd.horizontal_velocity)
#        print("yaw_rate ", cmd.yaw_rate)
#        print("height", cmd.height)
#        print("pitch ", cmd.pitch)
#        print("roll ", cmd.roll)
        print("activation ", cmd.activation)
        print("hop_event ", cmd.hop_event)
        print("trot_event ", cmd.trot_event)
        print("activate_event ", cmd.activate_event)


    def dogbot(self,use_imu=False):
        """Main program
        """
        led=Led()
        #Red wipe
        led.colorChange(255, 0, 0)
        #time.sleep(12)

        oled=Oled()
        oled.show_text("robot dog start...")
        # Create config
        config = Configuration()
        hardware_interface = HardwareInterface()

        # Create imu handle
        if use_imu:
            imu = IMU(port="/dev/serial0")
            imu.flush_buffer()

        # Create controller and user input handles
        controller = Controller(
            config,
            four_legs_inverse_kinematics,
        )
        state = State()
        print("Creating joystick listener...")
        oled.show_text("Creating joystick listener...")
        joystick_interface = JoystickInterface(config)
        print("Done.")
        #White wipe
        led.colorChange(255, 255, 255)

        last_loop = time.time()

        print("Summary of gait parameters:")
        print("overlap time: ", config.overlap_time)
        print("swing time: ", config.swing_time)
        print("z clearance: ", config.z_clearance)
        print("x shift: ", config.x_shift)

        # Wait until the activate button has been pressed
        while True:
            #Blue wipe
            #print ("\nBlue wipe")
            led.colorChange(0, 0, 255) 
            print("Waiting for L1 to activate robot.")
            oled.show_text("Waiting for L1 to activate robot.")
            while True:
                command = joystick_interface.get_command(state)
                #self.cmd_dump(command)
                joystick_interface.set_color(config.ps4_deactivated_color)
                if command.activate_event == 1:
                    break
                time.sleep(0.1)
            #Green wipe
            led.colorChange(0, 255, 0) 
            print("Robot activated.")
            oled.show_text("Robot activated.")

            joystick_interface.set_color(config.ps4_color)

            while True:
                now = time.time()
                if now - last_loop < config.dt:
                    continue
                last_loop = time.time()

                # Parse the udp joystick commands and then update the robot controller's parameters
                command = joystick_interface.get_command(state)
                #self.cmd_dump(command)
                if command.activate_event == 1:
                    print("Deactivating Robot")
                    oled.show_text("Deactivating Robot.")
                    #Blue wipe
                    led.colorChange(0, 0, 255) 
                    break

                # Read imu data. Orientation will be None if no data was available
                quat_orientation = (
                    imu.read_orientation() if use_imu else np.array([1, 0, 0, 0])
                )
                state.quat_orientation = quat_orientation

                # Step the controller forward by dt
                controller.run(state, command)

                # Update the pwm widths going to the servos
                hardware_interface.set_actuator_postions(state.joint_angles)


#if __name__ == '__main__':
    #time.sleep(10)
rbt=robot()
rbt.dogbot()
