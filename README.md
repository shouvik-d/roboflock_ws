# roboflock_ws

ROS2 (Humble) workspace for Roboflock: a rocker-bogie rover that follows a
handheld/wearable GPS "beacon" at walking speed, using Nav2 for autonomy.
LIDAR (RPLIDAR A1) provides local obstacle avoidance and feeds SLAM Toolbox's
occupancy grid; a dual `robot_localization` EKF fused with GPS provides the
robot's global position; ultrasonic sensors are an independent low-level
safety failsafe.

More background and hardware setup guides: <https://roboflock-documentation.readthedocs.io/en/latest/>

## Architecture

- **Beacon → rover link**: the beacon carries a u-blox ZED-F9P GPS wired
  directly to an HC-12 radio in transparent serial pass-through mode. The
  rover's matching HC-12 is wired to a Jetson UART (`/dev/ttyTHS1`) and read
  by `nmea_navsat_driver` exactly as if a GPS were locally attached
  (`beacon_pkg/launch/beacon_receiver.launch.py`) — publishing
  `/gps/beacon/fix`.
- **Rover's own GPS**: a u-blox NEO-M8P on USB, read by a second
  `nmea_navsat_driver` instance — publishing `/gps/robot/fix`
  (`bring_up/launch/robot_gps.launch.py`).
- **Localization**: `robot_localization`'s dual-EKF + `navsat_transform_node`
  pattern (`bring_up/launch/localization.launch.py`,
  `config/ekf_navsat_params.yaml`). The odom-frame EKF fuses IMU + rf2o
  scan-matching odometry and owns `odom→base_link`. The map-frame EKF fuses
  everything plus GPS and is the **sole owner of `map→odom`** — SLAM
  Toolbox runs alongside for its `/map` occupancy grid (local costmap
  obstacle data) but does not publish TF (`transform_publish_period: 0.0`
  in `config/slam_params.yaml`). This keeps Nav2's `map` frame geographically
  referenced, which beacon-following depends on.
- **Beacon → goal**: `beacon_pkg`'s `beacon_goalpose` node converts each
  `/gps/beacon/fix` into a `/goal_pose` by calling `navsat_transform_node`'s
  `/fromLL` service — this expresses the beacon's position in the *same*
  map frame Nav2 is actually using, anchored to the rover's own GPS datum.
  New goals are debounced (default 0.4 m) so GPS jitter doesn't cause
  constant replanning.
- **Nav2**: standard planner/controller/behavior/bt_navigator stack tuned
  for a non-holonomic 4-wheel differential-drive base (see
  `bring_up/config/nav2_params.yaml`), driven off `/goal_pose`.
- **Velocity arbitration**: `twist_mux` merges Nav2's output (`/cmd_vel_nav`),
  joystick teleop (`/cmd_vel_joy`), and the ultrasonic e-stop
  (`/cmd_vel_estop`, highest priority) into the `/cmd_vel` that
  `diff_drive_controller` (ODrive-driven, 4-wheel diff-drive) actually
  drives on.
- **Safety**: `ultrasonic_pkg` publishes `sensor_msgs/Range` per sensor;
  `bring_up`'s `ultrasonic_estop` node zeroes velocity via twist_mux
  whenever any reading is below a safe distance, independent of Nav2/LIDAR.

## Running

Full autonomy stack:

```
ros2 launch bring_up bringup.launch.py
```

Manual/standalone teleop only (no GPS/Nav2), e.g. for hardware bring-up:

```
./src/bring_up/bring_up/bring_up.sh
```

## Known limitations / out of scope

- **Meshtastic + the GPS visualization dashboard are not implemented in
  this repo.** The docs describe a separate, non-ROS system (three
  Meshtastic radios + a Flask dashboard, `jetsonBoth.py`/`tomBoth.py`) for
  command/status messaging and map visualization. Only the ROS2/HC-12/Nav2
  autonomy loop lives here.
- **Gazebo/Ignition simulation is unsupported/legacy.**
  `urdf_description/launch/gazebo.launch.py` and `robot_control.launch.py`
  are from an incomplete Gazebo-Classic → Ignition migration (see
  `urdf_description/GAZEBO_IGNITION_MIGRATION.md`) and are not maintained,
  since the physical hardware exists and is the deployment target.
  `urdf_description/launch/display.launch.py` (URDF + RViz, no Gazebo) does
  work and is useful for checking the robot model.
