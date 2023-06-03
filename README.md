# RT1_Assignment3
# Submitted by Shima Amiri Fard & Supervised by Prof. Carmine Recchiuto

__Sphinx Documentation__
For this project i developed documentation using Sphinx tool.
[SPHINX DOCUMENTAION](https://shimaamiri.github.io/RT_MoultimodalRobot/)

__Jupyter Notebook User Interface__
For this project i developed a Jupyter Notebook User Interface which can control the Robot. The user can choose the robot's mode.
[Jupyter Notebook](UI_Jupyter.ipynb)


__AIM OF THE ASSIGNMENT__
The assignment focuses on the development of a software architecture for the control of a mobile robot. Moreover, the architecture should also be able to fetch the request from the user.It must also allow the user to execute some of the behaviors.

In this assignment, we need to create a package in which the user will be able to use three different modalities in order to move the robot.The modalities are as follows:

+ autonomously reach a x,y coordinate inserted by the user
+ let the user drive the robot with the keyboard
+ let the user drive the robot assisting them in order to avoid collisions

We proceed in accordance with the instructions given to us beforehand (for example,setting the field goal and position coordinates, etc ) .

__PACKAGES USED__

The two packages responsible for localizing and planning the motion of the robot are `move_base` and `gmapping` packages which are briefly described below :

* The `move_base` package provides an implementation of an *action* that, given a goal in the world, the robot will try to reach it with a mobile base.

* The `gmapping` package contains the algorithm based on a *particle filter* (approach to estimate a probability density) needed for implementing Simultaneous Localization and Mapping (SLAM). Needed by the `gmapping` package. 

The package will be tested on a simulation of a mobile robot driving inside of a given environment. The simulation and visualization are run by the two following programs: 

* **Rviz**: which is a tool for ROS Visualization. Given below is the Rviz environment:

![Rviz](rviz_simulation.png)

* **Gazebo**: It is a free and open source robot simulation environment. 

Given below is the Gazebo Environmnet:

![Gazebo](map_Assgn3.png)

__INSTALLATION AND SIMULATION__

The project runs on the ROS Noetic environment.

The simulation requires the following steps before running:

* A [ROS Noetic](http://wiki.ros.org/noetic/Installation) installation,

* The download of the `slam_gmapping` package form the *Noetic* branch of the [Professor's repository](https://github.com/CarmineD8/slam_gmapping.git )

Run the following command from the shell:
```bash
git clone https://github.com/CarmineD8/slam_gmapping.git
```

* The download of the **ROS navigation stack** 

Run the following command from the shell:
```bash
sudo apt-get install ros-<your_ros_distro>-navigation
```

* And the and the clone of the [Current repository](https://github.com/shimaamiri/RT1_Assignment3 ). After downloading the repository, you should take the `final_assignment` directory included in the repository and place it inside the local workspace directory.

Run the following command from the shell:
```bash
git clone https://github.com/shimaamiri/RT1_Assignment3
```
Now, run the final commands to launch the platform 
```bash
roslaunch final_assignment simulation_gmapping.launch
```
Run the move.base launch file
```bash
roslaunch final_assignment move_base.launch
```
In order to run the final aspect of the assignment, enter the command in the terminal:
```bash
roslaunch final_assignment launch_files.launch
```

The *Python* scripts developed define a **user interface** that will let the user switch between driving modalities.

The **four scripts** provided are the following: 

+ UI.py
+ auto.py
+ manual.py
+ assistive.py


__NODES DESCRIPTION__
	
__UI__
The user can easily switch bewtween modalities including the one with the idle state. The node is responsible for driving the robot. The user can give the keyboard inputs while interacting.

Driving modalities related to their keyboard inputs are:

 + The following keyboard input [0] resets the current driving modality.
 + The following keyboard input [1] will start the autonomous drive towards a certain location in the map chosen by the user.
 + The following keyboard input [2] is a manual mode without even requiring any assistance.
 + The following keyboard input [3] is a manual mode  but this case requires an assistance.
 + The following keyboard input [4]quits the process.


__Auto Driving__

This is the implementation of the __'Autonomous Driving modality'__ feature. The user is asked to insert the __'x'__ and __'y'__ coordinates in which the robot will navigate. If the request cannot be fulfilled within 60 seconds the goal will be cancelled for which a 60 seconds timer is set. The user can also cancel the goal before the time is over, it is sufficient to return to the __'idle'__ status by pressing '0' on the UI console (also shown in the flowchart).

__Manual Driving__

This is the implementation of the Driving with and without assistance. It checks whether there is an obstacle or the path is clear.The user can quit both the modalities by pressing p from the console or by pressing a command on the user-interface.


__FlowChart__

![Flowchart](Flowchart_RT1_3.png)

__Conclusion and Improvements__
+ We can clearly see in some of the cases that the robot seems to not choose the best possible path. Hence, there can be a modification where the robot's direction can be manually adjusted while it is autonomously moving.

+ Also,the User Interface could be enhanced for a better user experience.Moreover, the robot can only see within+-90 relative degrees range, so avoiding obstacle while moving backward is a major issues.
 
+ The visual range of the robot can be extended in cases where the robot has passed the goal and needs to turn around in order to reach the position(assuming the goal is behind the robot).


