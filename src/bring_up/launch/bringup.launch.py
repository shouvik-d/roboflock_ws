#!/usr/bin/env python3

import os
from launch import LaunchDescription
import launch
from launch.actions import (
	DeclareLaunchArgument,
	EmitEvent,
	LogInfo,
	ExecuteProcess,
	RegisterEventHandler,
	TimerAction,
	GroupAction,
	IncludeLaunchDescription,
	SetEnvironmentVariable
)
from launch.conditions import IfCondition
from launch.event_handlers import (
	OnExecutionComplete,
	OnProcessExit,
	OnProcessIO,
	OnProcessStart,
	OnShutdown
)
from launch.events import Shutdown
from launch.substitutions import (
	EnvironmentVariable,
	FindExecutable,
	LaunchConfiguration,
	LocalSubstitution,
	PythonExpression,
	PathJoinSubstitution,
	TextSubstitution,
	Command
)
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
	# Paths to launch files >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	imu_launch_file = os.path.join(
		get_package_share_directory('bring_up'),
		'launch',
		'mpu9250driver_launch.py'
	)
	
	lidar_launch_file = os.path.join(
		get_package_share_directory('rplidar_ros'),
		'launch',
		'rplidar_a1_launch.py'
	)
	
	ultrasonic_launch_file = os.path.join(
		get_package_share_directory('ultrasonic_pkg'),
		'launch',
		'ultrasonic_publisher.launch.py'
	)
	
	battery_launch_file = os.path.join(
		get_package_share_directory('bring_up'),
		'launch',
		'battery_monitor.launch.py'
	)
	
	motor_launch_file = os.path.join(
		get_package_share_directory('motor_controller_pkg'),
		'launch',
		'motor_controller.launch.py'
	)
	
	beacon_launch_file = os.path.join(
		get_package_share_directory('beacon_pkg'),
		'launch',
		'beacon_receiver.launch.py'
	)
	
	goalpose_launch_file = os.path.join(
		get_package_share_directory('beacon_pkg'),
		'launch',
		'beacon_goalpose.launch.py'
	)
	
	robot_gps_launch_file = os.path.join(
		get_package_share_directory('bring_up'),
		'launch',
		'robot_gps.launch.py'
	)
	
	laser_odom_launch_file = os.path.join(
		get_package_share_directory('rf2o_laser_odometry'),
		'launch',
		'rf2o_laser_odometry.launch.py'
	)
	
	nav2_launch_file = os.path.join(
		get_package_share_directory('bring_up'),
		'launch',
		'nav2.launch.py'
	)
	
	description_launch_file = os.path.join(
		get_package_share_directory('roboflock_description'),
		'launch',
		'robot_state_publisher.launch.py'
	)
	
	localization_launch_file = os.path.join(
		get_package_share_directory('bring_up'),
		'launch',
		'localization.launch.py'
	)
	
	slam_launch_file = os.path.join(
		get_package_share_directory('bring_up'),
		'launch',
		'slam.launch.py'
	)
	
	
	# Launch args >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	declare_autostart = DeclareLaunchArgument(
		'autostart',
		default_value='true',
		description='Automatically start the navigation stack'
	)
	
	declare_slam = DeclareLaunchArgument(
		'slam',
		default_value='true',
		description='Run SLAM if true, else use existing map'
	)
	
	declare_use_xacro = DeclareLaunchArgument(
		'use_xacro',
		default_value='true',
		description='If true, use xacro to process the URDF'
	)
	
	urdf_file = os.path.join(
		get_package_share_directory('roboflock_description'),
		'urdf',
		'robot.urdf.xacro'
	)
    
	# 0.) Static Transforms >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	robot_description_content = ParameterValue(
		Command([
			FindExecutable(name='xacro'), ' ', urdf_file
		]) if LaunchConfiguration('use_xacro') else Command([
			'cat ', urdf_file
		]),
		value_type=str
	)
	
	
	static_tf_node = GroupAction([
		LogInfo(msg="*** Starting Static Transforms ***"),
		
		IncludeLaunchDescription(
			PythonLaunchDescriptionSource(description_launch_file),
		),
	])
	
	
	# 1.) Beacon/GPS System >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	gps_nodes = GroupAction([
		LogInfo(msg="*** Starting GPS and Beacon Connection ***"),
		
		IncludeLaunchDescription(
			PythonLaunchDescriptionSource(beacon_launch_file),
		),
		
		IncludeLaunchDescription(
			PythonLaunchDescriptionSource(robot_gps_launch_file),
		),
	])
	

	# 2.) Sensor nodes >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	sensor_nodes = GroupAction([
		LogInfo(msg='*** Starting Sensor Nodes ***'),
		
		IncludeLaunchDescription(
			PythonLaunchDescriptionSource(imu_launch_file)
		),
		
		IncludeLaunchDescription(
			PythonLaunchDescriptionSource(lidar_launch_file),
		),
        
        IncludeLaunchDescription(
        	PythonLaunchDescriptionSource(ultrasonic_launch_file),
        ),
        
        IncludeLaunchDescription(
        	PythonLaunchDescriptionSource(battery_launch_file),
        )
	])
	
	
	# 3.) Robot Localization >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	
	localization_nodes = GroupAction([
		LogInfo(msg="*** Starting Localization ***"),
		
		IncludeLaunchDescription(
			PythonLaunchDescriptionSource(localization_launch_file),
		),
		
		IncludeLaunchDescription(
			PythonLaunchDescriptionSource(laser_odom_launch_file)
		),
	])
	
	
	# 4.) SLAM Toolbox >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	
	slam_node = GroupAction([
		LogInfo(msg="*** Starting SLAM Toolbox ***"),
		
		IncludeLaunchDescription(
			PythonLaunchDescriptionSource(slam_launch_file),
		),
	])
	
	
	# 5.) Motor Controller >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	
	motor_node = GroupAction([
		LogInfo(msg="*** Starting Motor Controller ***"),
		
		IncludeLaunchDescription(
			PythonLaunchDescriptionSource(motor_launch_file),
		),
	])
	
	
	# 6.) Nav2 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	
	nav2_node = GroupAction([
		LogInfo(msg="*** Starting Nav2 ***"),
		
		IncludeLaunchDescription(
			PythonLaunchDescriptionSource(nav2_launch_file),
		),
		
		IncludeLaunchDescription(
			PythonLaunchDescriptionSource(goalpose_launch_file),
		),
	])
	
	
	return launch.LaunchDescription([
		declare_autostart,
		declare_slam,
		declare_use_xacro,
		
		static_tf_node,	
		gps_nodes,
		
		# GPS & HC-12 nodes should launch separately since the
		# event handler can only distinguish one event at a time
		RegisterEventHandler(
			event_handler=OnProcessIO(
				target_action=gps_nodes,
				on_stdout=lambda event: LogInfo(
					msg=f"Found: {event.text.decode()}"
				),
				on_stdout_regex=r"*GPS nodes initialized*",
				on_start=sensor_nodes
			)
		),
		
		
		RegisterEventHandler(
			event_handler=OnProcessIO(
				target_action=sensor_nodes,
				on_stdout=lambda event: LogInfo(
					msg=f"Found: {event.text.decode()}"
				),
				on_stdout_regex=r"*Ultrasonic Publisher initialized*",
				on_start=localization_nodes
			)
		),
		
		RegisterEventHandler(
			event_handler=OnProcessIO(
				target_action=localization_nodes,
				on_stdout=lambda event: LogInfo(
					msg=f"Found: {event.text.decode()}"
				),
				on_stdout_regex=r"*Localization nodes initialized*",
				on_start=slam_node
			)
		),
		
		RegisterEventHandler(
			event_handler=OnProcessIO(
				target_action=slam_node,
				on_stdout=lambda event: LogInfo(
					msg=f"Found: {event.text.docode()}"
				),
				on_stdout_regex=r"*SLAM toolbox node intialized*",
				on_start=motor_node
			)
		),
		
		RegisterEventHandler(
			event_handler=OnProcessIO(
				target_action=motor_node,
				on_stdout=lambda event: LogInfo(
					msg=f"Found: {event.text.decode()}"
				),
				on_stdout_regex=r"Motors initialized*",
				on_start=nav2_node
			)
		),
		
		RegisterEventHandler(
			event_handler=OnProcessIO(
				target_action=nav2_node,
				on_stdout=lambda event: LogInfo(
					msg=f"Found: {event.text.decode()}"
				),
				on_stdout_regex=r"Nav2 initialized*",
				on_start=None
			)
		)
				
    ])
	
	
if __name__ == '__main__':
	generate_launch_description()