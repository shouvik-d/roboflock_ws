# Quick Comparison: Gazebo Classic vs Gazebo Ignition

## Key Differences in URDF_description Package

### 1. Control System
| Aspect | Gazebo Classic | Gazebo Ignition |
|--------|----------------|-----------------|
| **Control Plugin** | gazebo_ros2_control | ignition-gazebo-diff-drive-system |
| **Configuration** | ros2_control YAML + URDF tags | Plugin parameters in .gazebo file |
| **Controllers** | Separate spawner nodes | Built into Gazebo plugin |
| **Joint Control** | ros2_control interfaces | Direct Gazebo control |

### 2. Launch Files
| Component | Gazebo Classic | Gazebo Ignition |
|-----------|----------------|-----------------|
| **Gazebo Launch** | gazebo_ros/gazebo.launch.py | ros_gz_sim/gz_sim.launch.py |
| **Spawn Robot** | gazebo_ros/spawn_entity.py | ros_gz_sim/create |
| **Topic Bridge** | Not needed (native) | ros_gz_bridge required |
| **Controllers** | controller_manager/spawner | Not needed |

### 3. Plugins in URDF
| Plugin Type | Gazebo Classic | Gazebo Ignition |
|-------------|----------------|-----------------|
| **Diff Drive** | libgazebo_ros2_control.so | ignition-gazebo-diff-drive-system |
| **Sensors** | gazebo_ros_ray (lidar) | ignition-gazebo-sensors-system |
| **TF Publishing** | Via ros2_control | ignition-gazebo-pose-publisher-system |

### 4. Topic Names
| Data | Gazebo Classic | Gazebo Ignition |
|------|----------------|-----------------|
| **Odometry** | /odom (direct) | /model/my_bot/odometry → /odom (bridged) |
| **Cmd Vel** | /cmd_vel (direct) | /cmd_vel (bridged) |
| **Lidar** | /scan (direct) | /scan (bridged) |
| **TF** | /tf (direct) | /model/my_bot/tf → /tf (relayed) |
| **Clock** | /clock (direct) | /clock (bridged) |

## What Stayed the Same ✅
- Robot URDF structure (all links and joints)
- Mesh files and visual/collision geometry
- Inertial properties
- Joint types and axes
- Robot dimensions and mass properties
- Wheel configuration (4-wheel differential drive)

## What Changed 🔄
- Gazebo plugin system (Classic → Ignition)
- Control architecture (ros2_control → built-in diff drive)
- Launch file structure
- Topic bridging mechanism
- Sensor plugin syntax

## Migration Benefits 🚀
1. **Better Performance**: Ignition has improved physics and rendering
2. **Modern Architecture**: More modular plugin system
3. **Active Development**: Ignition is the future of Gazebo
4. **Better Sensors**: Improved sensor simulation
5. **Distributed Simulation**: Support for multi-robot scenarios

## Testing Checklist ✓
- [ ] Robot spawns correctly in Gazebo Ignition
- [ ] Wheels rotate when sending /cmd_vel commands
- [ ] Odometry is published on /odom topic
- [ ] Lidar data appears on /scan topic
- [ ] TF tree is complete (odom → base_link)
- [ ] Robot responds to teleop commands
- [ ] RViz displays robot correctly with use_sim_time:=true
