#!/bin/bash
source /opt/ros/humble/setup.bash
cd /home/roboflock/roboflock_ws/   # absolute path
source install/setup.bash

ros2 run joy joy_node &            # background it so script continues
ros2 run bring_up self_destruct &
ros2 run bring_up diff_drive_controller

