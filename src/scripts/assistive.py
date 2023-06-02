#!/usr/bin/env python3

"""
.. module:: assistive
    :platform: Unix
    :synopsis: Python module for assistive driving.
.. moduleauthor:: Shima Amiri Fard <s5269794@studenti.unige.it>

This module implements the third mode of the assistive driving, where the robot can be controlled manually by the user. Moreover, obstacles are detected by a laser scanner to avoid collisions.

Subscribes to:
    - /laser_scan

Publishes to:
    - /avoid
"""

from __future__ import print_function
from sensor_msgs.msg import LaserScan
import rospy
from final_assignment.msg import Avoid


l = True  # wall on the left
r = True  # wall on the right
f = True  # wall in front


def callback_avoid(msg):
    """
    Callback function to retrieve data from the obstacles (walls) surrounding the robot. This function receives data from
    /laser_scan, and divides the data into five ranges: right, front-right, front, front-left, and left.

    Args:
        msg (sensor_msgs.msg.LaserScan): Contains the distances from obstacles.
    """

    global l, r, f

    active_ = rospy.get_param("/active")  # Active parameters value is assigned to the local variables

    if active_ == 3:

        right = min(msg.ranges[0:143])
        front = min(msg.ranges[288:431])
        left = min(msg.ranges[576:719])

        if right < 1.0:  # robot on the right
            r = False
        else:
            r = True

        if front < 1.0:  # robot on the front
            f = False
        else:
            f = True

        if left < 1.0:  # robot on the left
            l = False
        else:
            l = False

    # If all the conditions are okay, Operation 3 "Obstacle avoidance operations to drive
    # the robot assisting them (using keyboard) to avoid collisions" is stopped
    else:
        r = True
        f = True
        l = True


def main():
    """
    Main function which controls the robot's behavior. The subscriber, publisher are created and the node is initialized.
    """

    global l, r, f

    # Publishing
    pub = rospy.Publisher('custom_controller', Avoid, queue_size=10)  # publisher to custom_controller
    rospy.init_node('avoidance')  # initializing the node
    sub = rospy.Subscriber('/scan', LaserScan, callback_avoid)  # subscriber to /scan
    rate = rospy.Rate(5)

    pub_msg = Avoid()  # custom message

    while not rospy.is_shutdown():
        pub_msg.left = l  # custom message field is assigned for left wall
        pub_msg.right = r  # custom message field is assigned for right wall
        pub_msg.front = f  # custom message field is assigned for front wall

        pub.publish(pub_msg)  # publishing

        rate.sleep()


if __name__ == "__main__":
     main()

