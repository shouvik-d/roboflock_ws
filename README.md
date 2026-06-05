# Roboflock — Autonomous Mobile Robot (ROS 2)

The complete ROS 2 workspace for **Roboflock**, an autonomous four-wheel differential-drive robot that navigates in real time by fusing LiDAR and GPS. This repo holds the source; the full write-up, setup, and architecture live in the documentation site below.

**[Read the full documentation »](https://roboflock-documentation.readthedocs.io/en/latest/)**

<!-- Add a short demo clip or photo of the robot here:
![Roboflock](docs/roboflock.jpg) -->

## What it does
- Autonomous navigation with **Nav2**, **SLAM**, and `robot_localization`, fusing **LiDAR + GPS**.
- Custom **ROS 2 nodes** for 2D LiDAR visualization and a differential-drive controller interfaced with **ODrive** motor modules.
- Microcontroller-driven **ultrasonic sensing** as an independent obstacle-detection failsafe.
- Runs on an **NVIDIA Jetson Orin Nano** with a custom-wired power and motor-driver stack.

## Stack
ROS 2 · C++ / Python · Nav2 · SLAM · robot_localization · ODrive · LiDAR · GPS · NVIDIA Jetson Orin Nano

## Repository layout
```
src/    ROS 2 packages (nodes, controllers, launch, config)
```

## Build
Standard ROS 2 colcon workspace:
```bash
cd roboflock_ws
colcon build
source install/setup.bash
```
See the [documentation](https://roboflock-documentation.readthedocs.io/en/latest/) for dependencies, hardware setup, and launch instructions.
