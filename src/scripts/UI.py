#!/usr/bin/python3

"""
.. module:: UI
    :platform: Unix
    :synopsis: Python module for choosing driving mode
.. moduleauthor:: Shima Amiri Fard <s5269794@studenti.unige.it>

The user Interface node provides the users options to choose their desired driving mode (Auto mode, Manual mode, Assistive mode, and idle mode). 


The main parameters are:

**Active**: According to the user input, the value of this parameter will change. All nodes either keep their current idle state or switch to a running state. 

**(X, Y)**: If the mode [1] is chosen (auto mode), the User interface asks a target X and Y coordinate from the user.
"""

from std_srvs.srv import *
import math
import rospy


msg = """
**Driving Modes**
#Press 1: Auto Mode, drives the robot autonomously to x, y coordinates
#Press 2: Manual Mode, user can drive the robot using the keyboard
#Press 3: Assistive Mode, user can assist the robot while it is moving to avoid obstacles. 
#Press 0: Idle Mode, the robot doesn't move and waits for user commands.

q/z: accelerate/decelerate velocity by 10%
w/x: accelerate/decelerate only linear velocity by 10%
e/c: accelerate/decelerate only angular velocity by 10%

CTRL-C to quit
"""


def main():
    """
    Main function asks the user to choose the driving mode (Auto mode, Manual mode, Assistive mode, or idle mode). 
    """
    f = False  # goal termination 
    while not rospy.is_shutdown():
        command = int(input('Please choose the driving mode: '))

        # 1: auto mode, drives the robot autonomously to x, y coordinates
        if command == 1:
            if f == True:
                f = False

            rospy.set_param('active', 0)

            print("Enter the desired coordinate you want the robot to reach (x, y)")
            pos_x = float(input("Enter X: "))
            pos_y = float(input("Enter Y: "))  

            rospy.set_param('des_pos_x', pos_x)  
            rospy.set_param('des_pos_y', pos_y)  
            rospy.set_param('active', 1)
            f = True

        # 2: manual mode, user can drive the robot using the keyboard
        elif command == 2:
            if f == True:
                f = False

            rospy.set_param('active', 2)

        # 3: assistive mode, user can assist the robot while it is moving to avoid obstacles.
        elif command == 3:
            if f == True:
                f = False

            rospy.set_param('active', 3)

        # 4: idle mode, the robot doesn't move and waits for user commands.
        elif command == 0:
            if f == True:
                f = False

            rospy.set_param('active', 0)

        else:
            print("Wrong key!!!")


if __name__ == '__main__':
    print(msg)
    main()

