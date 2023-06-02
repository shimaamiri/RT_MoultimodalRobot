#!/usr/bin/env python3

"""
.. module:: manual
    :platform: Unix
    :synopsis: Python module for manual driving
.. moduleauthor:: Shima Amiri Fard <s5269794@studenti.unige.it>

This node uses "teleop_twist_keyboard.py", refer to <http://wiki.ros.org/teleop_twist_keyboard> . This allows the user to drive the robot manually by pressing keys, then depending on the input this node publishes twist message on the /cmd_vel topic. The Twist message defines the linear and angular velocity of the robot. 

Publishes to:
  /cmd_vel 
"""

from __future__ import print_function

import threading
from sensor_msgs.msg import LaserScan
import roslib; roslib.load_manifest('teleop_twist_keyboard')
import rospy

from final_assignment.msg import Avoid

from geometry_msgs.msg import Twist
import time
from std_srvs.srv import *
import sys, select, termios, tty


msg = """
MANUAL DRIVING MODE
---------------------------
Moving around:
           k   
      j    i    l 

For Holonomic mode (strafing), hold down the shift key:
---------------------------
           K    
      U    I    L


q/z : accelerate/decelrate velocity by 10%
w/x : accelerate/decelrate only linear velocity by 10%
e/c : accelerate/decelrate only angular velocity by 10%

CTRL-C to quit
"""

l = True  # the wall at the left of the robot
r = True  # the wall at the right of the robot
f = True  # the wall at the front of the robot
fl = True # the wall at the front-left of the robot 
fr = True # the wall at the front-right of the robot
moveBindings = {
        'i':(1,0,0,0),
        'o':(1,0,0,-1),
        'j':(0,0,0,1),
        'l':(0,0,0,-1),
        'u':(1,0,0,1),
        'k':(-1,0,0,0),
        '.':(-1,0,0,1),
        'm':(-1,0,0,-1),
        'O':(1,-1,0,0),
        'I':(1,0,0,0),
        'J':(0,1,0,0),
        'L':(0,-1,0,0),
        'U':(1,1,0,0),
        'K':(-1,0,0,0),
        '>':(-1,-1,0,0),
        'M':(-1,1,0,0),
        't':(0,0,1,0),
        'b':(0,0,-1,0),
    }

speedBindings={
        'q':(1.1,1.1),
        'z':(.9,.9),
        'w':(1.1,1),
        'x':(.9,1),
        'e':(1,1.1),
        'c':(1,.9),
    }

class PublishThread(threading.Thread):
    def __init__(self, rate):
        super(PublishThread, self).__init__()
        self.publisher = rospy.Publisher('cmd_vel', Twist, queue_size = 1)
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.th = 0.0
        self.speed = 0.0
        self.turn = 0.0
        self.condition = threading.Condition()
        self.done = False


        if rate != 0.0:
            self.timeout = 1.0 / rate
        else:
            self.timeout = None

        self.start()

    def wait_for_subscribers(self):
        """
        A function to wait for subscribers
        """
        i = 0
    
        while not rospy.is_shutdown() and self.publisher.get_num_connections() == 0:
            if i == 4:
                print("waiting for the subscribers ...".format(self.publisher.name))
            rospy.sleep(0.5)
            i = i + 1
            i = i % 5
        if rospy.is_shutdown():
            raise Exception("shutdown request")

    def update(self, x, y, z, th, speed, turn):
        """
        A funtion for updating the coordinate and velocity of the robot.
          
        Args:
	      x
          y
          z 
          th: threshold
          speed
          turn 	 
        """   
        self.condition.acquire()
        self.x = x
        self.y = y
        self.z = z
        
        self.th = th
        self.speed = speed
        self.turn = turn
        
        self.condition.notify()
        self.condition.release()

    def stop(self):
        self.done = True
        self.update(0, 0, 0, 0, 0, 0)
        self.join()

    def stop_r(self):
        """
        This function is used by "PublishThread" class. It will stop the robot by turning the linear and angular velocities to 0 with the "Twist" message through the "/cmd_vel" topic.
        """
        twist = Twist()
        
        twist.linear.x = 0
        twist.linear.y = 0
        twist.linear.z = 0
        
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = 0
        
        self.publisher.publish(twist)

    def run(self):
        twist = Twist()
        while not self.done:
            self.condition.acquire()
            # Wait for a new message or timeout.
            self.condition.wait(self.timeout)

            # Copy state into twist message.
            twist.linear.x = self.x * self.speed
            twist.linear.y = self.y * self.speed
            twist.linear.z = self.z * self.speed
            twist.angular.x = 0
            twist.angular.y = 0
            twist.angular.z = self.th * self.turn

            self.condition.release()

            # Publish
            self.publisher.publish(twist)

        # stopped message is published when thread exits
        twist.linear.x = 0
        twist.linear.y = 0
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = 0
        self.publisher.publish(twist)
        

def input(key_timeout):
    """
	This funtion recieves inputs from the user via keyboard.
	
	Args:
	  key_timeout
	"""
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], key_timeout)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def CallBack_scan(msg):
	"""
	This callback function retrieves info from obstacles surrounding the robot.
	
	Subscribes to:
          /check topic, which publishes to /avoidingwall.msg, which contains the info about the walls near the robot. 
	
	"""
	global f, r, l, fl, fr
	
	f = msg.front
	r = msg.right
	l = msg.left
	fr = msg.fright
	fl = msg.fleft
	
def pop(dictionary):
    """
    This function associates the pressed key to the real motion of the robot by using POP command.
    
    Args: 
      dictionary(dict): a dictionary consisting of keys
    
    For each direction, value 1 means that the wall is not close in that direction so robot can turn in that direction. Value 0, means the  wall is closed to that direction so turn toward that direction is not allowed.

    """
    global f, r, l, fl, fr
    
    # check whether the wall is allowed in different directions. Otherwise, they will be omited from the dictionary.
    if not f == True and not r == True and not l == True:
        dictionary.pop('i')
        dictionary.pop('j')
        dictionary.pop('l')
        
    elif not l == True and not f == True and r == True:
        dictionary.pop('i')
        dictionary.pop('j')
        
    elif l == True and not f == True and not r == True:
        dictionary.pop('i')
        dictionary.pop('l')
        
    elif not l == True and f == True and not r == True:
        dictionary.pop('l')
        dictionary.pop('j')
        
    elif l == True and not f == True and r == True:
        dictionary.pop('i')
        
    elif not l == True and f == True and r == True:
        dictionary.pop('j')
        
    elif l == True and f == True and not r == True:
        dictionary.pop('l')
        

def vels(speed, turn):
    """
    This function reports the velocity of the robot
    
    Args: 
      speed
      turn
    """
    return ":\tspeed %s\tturn %s " % (speed,turn)


if __name__=="__main__":
    rospy.init_node('teleop') 
    # parameters
    settings = termios.tcgetattr(sys.stdin) 
    speed = rospy.get_param("~speed", 0.5)
    turn = rospy.get_param("~turn", 1.0)
    repeat = rospy.get_param("~repeat_rate", 0.0)
    key_timeout = rospy.get_param("~key_timeout", 0.1)    
    active_=rospy.get_param("/active") 
     
    rospy.Subscriber("check", Avoid, CallBack_scan)	
 
    flag1 = True									
    flag2 = False									

    if key_timeout == 0.0:
        key_timeout = None

    pub_thread = PublishThread(repeat)

    x = 0
    y = 0
    z = 0
    th = 0
    st = 0

    rate = rospy.Rate(5)
    pub_thread.wait_for_subscribers()
    pub_thread.update(x, y, z, th, speed, turn)
    moveBindings_temp = {}
    
    print(msg)				
    print(vels(speed,turn))		
    
    while not rospy.is_shutdown():
        	
        active_=rospy.get_param("/active") 
        moveBindings_temp = moveBindings.copy() 
        
        # status of modes
        if active_ == 2 or active_ == 3:		
        	
            if flag2 == False:
            	print("active mode "+ str(active_))
            	
            flag2 = True
            key = input(key_timeout)

            pop(moveBindings_temp)				
            if key in moveBindings_temp.keys():
                x = moveBindings_temp[key][0] 
                y = moveBindings_temp[key][1]
                z = moveBindings_temp[key][2]
                th = moveBindings_temp[key][3]

            elif key in speedBindings.keys():
                speed = speed * speedBindings[key][0]
                turn = turn * speedBindings[key][1]

                print(vels(speed,turn))
                if (st == 14):
                    print(msg)
                st = (st + 1) % 15
            else:
                # if key_reset and robot is stopped, /cmd_vel does not get updated
                if key == '' and x == 0 and y == 0 and z == 0 and th == 0:
                    continue
                x = 0
                y = 0
                z = 0
                th = 0
                if (key == '\x03'):
                    break

            pub_thread.update(x, y, z, th, speed, turn)
            flag = 1

        else:
            if flag1 == True:
                pub_thread.stop_r() 
                print("request is canceled!!")
            flag1 = False
            flag2 = False

        rate.sleep() 
            
