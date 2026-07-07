#!/bin/bash
# Manual/standalone teleop-only mode: joystick -> motors, no Nav2/twist_mux.
# For full autonomy, use `ros2 launch bring_up bringup.launch.py` instead.
source /opt/ros/humble/setup.bash
cd /home/roboflock/roboflock_ws/   # absolute path
source install/setup.bash

ros2 run joy joy_node &            # background it so script continues
ros2 run bring_up self_destruct --ros-args -p cmd_vel_topic:=cmd_vel &
ros2 run bring_up diff_drive_controller

