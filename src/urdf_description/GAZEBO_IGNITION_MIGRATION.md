# Gazebo Ignition Migration Summary

## Overview
This document summarizes the changes made to migrate the URDF_description package from Gazebo Classic to Gazebo Ignition (Gazebo Fortress/Garden).

## Files Modified

### 1. urdf/URDF.gazebo
**Changes:**
- **Removed:** Gazebo Classic sensor definitions and basic material properties
- **Added:** Gazebo Ignition plugins:
  - `ignition-gazebo-diff-drive-system`: Handles differential drive control for 4-wheel robot
  - `ignition-gazebo-pose-publisher-system`: Publishes TF transforms
  - `ignition-gazebo-sensors-system`: Manages lidar sensor
- **Updated:** Lidar sensor configuration with proper Ignition syntax and topic publishing
- **Enhanced:** Wheel friction properties with additional parameters (kp, kd, minDepth, maxVel, fdir1)

**Key Plugin Parameters:**
- Wheel joints: lf_wheel_to_coupling, lr_wheel_to_coupling, rf_wheel_to_coupling, rr_wheel_to_coupling
- Wheel separation: 0.64m
- Wheel radius: 0.1m
- Max linear velocity: 1.0 m/s
- Max angular velocity: 2.0 rad/s

### 2. urdf/URDF.xacro
**Changes:**
- **Removed:** Complete ros2_control configuration block
- **Removed:** gazebo_ros2_control plugin
- **Kept:** All robot links, joints, and physical structure unchanged

**Reason:** Gazebo Ignition uses its own built-in diff drive plugin instead of ros2_control for basic differential drive functionality.

### 3. launch/gazebo.launch.py
**Changes:**
- **Replaced:** `gazebo_ros` with `ros_gz_sim` for launching Gazebo Ignition
- **Replaced:** `spawn_entity.py` with `ros_gz_sim create` for spawning robot
- **Removed:** ros2_control controller spawners (joint_state_broadcaster, diff_drive_controller)
- **Added:** `ros_gz_bridge` for bridging Gazebo and ROS topics:
  - /cmd_vel (Twist messages)
  - /odom (Odometry)
  - /tf (Transforms)
  - /scan (LaserScan from lidar)
  - /clock (Simulation time)
- **Added:** TF relay node to republish Gazebo TF to ROS TF topic
- **Added:** TimerAction delays for proper startup sequence

## Robot Structure Preserved
✅ All robot chassis components remain unchanged:
- Base link and hull components
- Rocker-bogie suspension system
- All 4 wheels and their mounting
- Motors and couplings
- Pushrods and differential bar
- Lidar sensor link

## How to Use

### Build the package:
```bash
cd ~/ros2_ws
colcon build --packages-select URDF_description
source install/setup.bash
```

### Launch in Gazebo Ignition:
```bash
ros2 launch URDF_description gazebo.launch.py
```

### Control the robot:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## Topic Mapping
| Gazebo Ignition Topic | ROS 2 Topic | Message Type |
|----------------------|-------------|--------------|
| /cmd_vel | /cmd_vel | geometry_msgs/Twist |
| /model/my_bot/odometry | /odom | nav_msgs/Odometry |
| /model/my_bot/tf | /tf (via relay) | tf2_msgs/TFMessage |
| /scan | /scan | sensor_msgs/LaserScan |
| /clock | /clock | rosgraph_msgs/Clock |

## Dependencies Required
- ros-humble-ros-gz-sim
- ros-humble-ros-gz-bridge
- ros-humble-ros-gz-interfaces
- ignition-fortress (or gazebo-garden)

## Notes
- The diff_drive_controller.yaml config file is no longer used but kept for reference
- Joint states are now published by Gazebo Ignition's internal systems
- Odometry is computed by the diff drive plugin in Gazebo
- All simulation time is synchronized via /clock topic
