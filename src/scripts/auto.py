#!/usr/bin/env python
"""
.. module:: auto
    :platform: Unix
    :synopsis: Python module for autonomous driving.
.. moduleauthor:: Shima Amiri Fard <s5269794@studenti.unige.it>

This module implements the autonomous driving mode. In this node, an Action Client-Service communication is implemented.
The user needs to enter the target x and y, then the desired coordinate is sent as a goal to the action server/move_base.

Subscribes to:
    - /nav_msgs/odometry, which publishes the robot position

Action client:
    - /move_base

Action messages:
    - MoveBaseAction
    - MoveBaseGoal, contains information about where the robot should move to in the environment

Feedbacks:
    - /move_base/goal, if the goal is reached
    - /move_base/cancel, if the goal is canceled
"""

import time
import math
import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Twist, Point
from nav_msgs.msg import Odometry
from tf import transformations
from std_srvs.srv import *

state = "                                                                  "
flg = False


def param_update():
    """
    This function allocates updated values of parameters to the global variables.
    """
    global x_des, y_des, active_
    active_ = rospy.get_param('active')
    x_des = rospy.get_param('x_pos')
    y_des = rospy.get_param('y_pos')


def callback_odometry(msg):
    """
    A callback function to the topic /odom, which is required to retrieve the presence of the robot.
    The odometry information of the robot is stored in the r_pos variable.

    Args:
        msg: contains the position of the robot (x, y)
    """
    global r_pos
    r_pos = msg.pose.pose.position


def callback_status_update(status, result):
    """
    A callback function to update the robot status when it reaches the target.

    Args:
        status: goal status (actionlib_goalStatus)
        result: goal result (MoveBaseResult)
    """
    global flg

    if status == 3:
        print("GOAL REACHED!" + state)
        print("\n")
        flg = True


def client_goal():
    """
    This function sets a new goal for the robot. The action can send a goal or cancel request from the client to the server.
    After receiving, the server processes it and can give information back to the client.
    """
    goal.target_pose.pose.position.x = x_des
    goal.target_pose.pose.position.y = y_des
    print("AUTO MODE" + state)
    print("\n")
    client.send_goal(goal, callback_status_update)


def client_init():
    """
    This function first initializes the Action Client. Then waits for the server, and initializes and sets the goal message.
    """
    global client
    global goal

    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)

    client.wait_for_server()  # Waits until the server connects.
    goal = MoveBaseGoal()  # goal messages
    goal.target_pose.header.frame_id = "map"  # setting the goal message
    goal.target_pose.header.stamp = rospy.Time.now()
    goal.target_pose.pose.orientation.w = 1.0


def callback_reset(event):
    """
    This function will reset the robot's behavior when the robot doesn't reach the goal within a given time.

    Args:
        event: time variable
    """
    if active_ == 1:
        print("Goal time exceeded: " + str(event.current_real) + state)
        print("\n")
        print("Failed to reach the goal!!!")
        print("\n")
        # Setting parameters on the parameters server
        rospy.set_param('active', 0)


def main():
    """
    Main function which controls the robot's behavior.
    When the callback function subscribes and the node is initialized, the while loop starts spinning.
    During execution, the node will call the last defined functions as the robot state is defined by global variables.
    """
    active_ = rospy.get_param('active')  # active_ controls the robot's operation
    x_des = rospy.get_param('x_pos')  # retrieves the x component of the goal position
    y_des = rospy.get_param('y_pos')  # retrieves the y component of the goal position

    global flg
    rospy.init_node('go_to_desired_pos')  # initializing the node
    sub_odom = rospy.Subscriber('/odom', Odometry, callback_odometry)  # subscriber to /odom

    rate = rospy.Rate(10)  # sleep rate
    f1 = False
    f2 = False

    client_init()  # initializing the action client

    i = 0
    while 1:
        param_update()

        # If the active_ parameter is 1, the node gets active.
        if active_ == 1:
            if f1 == True:
                client_goal()  # sets a new goal
                rospy.Timer(rospy.Duration(40), callback_reset)  # initializing reset function

                f1 = False
                f2 = True

        else:
            # idle mode
            if f1 == False and f2 == False:
                print("OPERATION 1: Auto driving is stopped")
                print("\n")
                f1 = True

            if f1 == False and f2 == True:
                if flg == True:
                    # If the robot reaches the goal and the operation 1 is stopped
                    print("OPERATION 1: Auto driving is stopped" + state)
                    f1 = True
                    f2 = False
                    flg = False
                else:
                    # If the robot failed to reach the goal when the user starts the operations or else the time is exceeded.
                    print("Time exceeded!!! Failed to reach the goal!!! Operation 1 stopped!!! " + state)
                    client.cancel_goal()
                    f1 = True
                    f2 = False

        # robot position
        if i % 10 == 0:
            print("X-Coordinate " + str(r_pos.x) + " Y-Coordinate" + str(r_pos.y), end='\r')
        i = i + 1

        rate.sleep()


if __name__ == '__main__':
    main()

