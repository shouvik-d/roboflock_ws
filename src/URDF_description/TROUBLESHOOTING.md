# Troubleshooting Guide - Gazebo Ignition Migration

## Common Issues and Solutions

### 1. Robot Not Spawning
**Symptoms:** Launch file runs but robot doesn't appear in Gazebo

**Solutions:**
```bash
# Check if robot_description is being published
ros2 topic echo /robot_description --once

# Verify Gazebo Ignition is running
gz topic -l

# Check spawn command output for errors
# Look for URDF parsing errors in terminal
```

**Common Causes:**
- URDF syntax errors
- Missing mesh files
- Incorrect file paths in URDF

### 2. Robot Not Moving
**Symptoms:** Sending /cmd_vel commands but robot doesn't move

**Solutions:**
```bash
# Check if cmd_vel is being received
ros2 topic echo /cmd_vel

# Verify bridge is running
ros2 node list | grep parameter_bridge

# Check Gazebo topics
gz topic -l | grep cmd_vel

# Test with direct Gazebo command
gz topic -t /cmd_vel -m ignition.msgs.Twist -p "linear: {x: 0.5}"
```

**Common Causes:**
- Bridge not running or misconfigured
- Wrong joint names in diff drive plugin
- Wheel parameters incorrect (radius, separation)

### 3. No Odometry Data
**Symptoms:** /odom topic not publishing or empty

**Solutions:**
```bash
# Check if odometry is published in Gazebo
gz topic -l | grep odom

# Verify bridge configuration
ros2 node info /parameter_bridge

# Check remapping
ros2 topic list | grep odom
```

**Common Causes:**
- Bridge not configured for odometry topic
- Wrong model name in bridge arguments
- Diff drive plugin not loaded

### 4. Lidar Not Working
**Symptoms:** No data on /scan topic

**Solutions:**
```bash
# Check Gazebo lidar topic
gz topic -l | grep scan

# Verify sensor plugin is loaded
gz model -m my_bot -i

# Check bridge for scan topic
ros2 topic hz /scan
```

**Common Causes:**
- Sensor plugin not loaded
- Bridge missing scan topic
- Lidar link not properly attached

### 5. TF Tree Incomplete
**Symptoms:** Missing transforms, RViz shows errors

**Solutions:**
```bash
# View TF tree
ros2 run tf2_tools view_frames

# Check if tf_relay is running
ros2 node list | grep tf_relay

# Verify TF is being published
ros2 topic hz /tf
```

**Common Causes:**
- tf_relay node not running
- Pose publisher plugin not loaded
- use_sim_time not set correctly

### 6. Build Errors
**Symptoms:** colcon build fails

**Solutions:**
```bash
# Install missing dependencies
sudo apt update
sudo apt install ros-humble-ros-gz-sim ros-humble-ros-gz-bridge

# Clean build
cd ~/ros2_ws
rm -rf build/ install/ log/
colcon build --packages-select URDF_description

# Check for URDF syntax errors
check_urdf ~/ros2_ws/src/URDF_description/urdf/URDF.xacro
```

### 7. Simulation Time Issues
**Symptoms:** Nodes not synchronized, TF warnings

**Solutions:**
```bash
# Ensure all nodes use sim time
ros2 param get /robot_state_publisher use_sim_time
ros2 param get /rviz2 use_sim_time

# Check clock is being published
ros2 topic hz /clock

# Verify bridge includes clock
ros2 topic info /clock
```

**Fix:** Add `use_sim_time: True` to all node parameters

### 8. Performance Issues
**Symptoms:** Gazebo running slowly, lag

**Solutions:**
- Reduce sensor update rates in URDF.gazebo
- Simplify collision meshes
- Disable visualize on sensors during testing
- Use lower physics update rate

```xml
<!-- In URDF.gazebo, reduce update rates -->
<update_rate>5</update_rate>  <!-- Instead of 10 -->
```

## Debugging Commands

### Check All Topics
```bash
# ROS topics
ros2 topic list

# Gazebo topics
gz topic -l
```

### Monitor Topic Data
```bash
# ROS
ros2 topic echo /odom
ros2 topic hz /scan

# Gazebo
gz topic -e -t /model/my_bot/odometry
```

### Inspect Robot Model
```bash
# In Gazebo
gz model -m my_bot -i

# Check URDF
check_urdf ~/ros2_ws/src/URDF_description/urdf/URDF.xacro
```

### View Logs
```bash
# ROS logs
ros2 run rqt_console rqt_console

# Gazebo logs
gz log -i
```

## Quick Fixes

### Reset Simulation
```bash
# Kill all nodes
pkill -9 gz
pkill -9 ros2

# Restart
ros2 launch URDF_description gazebo.launch.py
```

### Rebuild Package
```bash
cd ~/ros2_ws
colcon build --packages-select URDF_description --symlink-install
source install/setup.bash
```

### Verify Installation
```bash
# Check Gazebo Ignition
gz sim --version

# Check ROS-Gazebo bridge
ros2 pkg list | grep ros_gz

# Check dependencies
rosdep check URDF_description
```

## Getting Help

If issues persist:
1. Check Gazebo Ignition logs: `~/.ignition/gazebo/log/`
2. Review ROS logs: `~/.ros/log/`
3. Verify URDF with: `check_urdf URDF.xacro`
4. Test with simple world first: `gz sim empty.sdf`
5. Compare with working urdf_description in ws/ workspace
