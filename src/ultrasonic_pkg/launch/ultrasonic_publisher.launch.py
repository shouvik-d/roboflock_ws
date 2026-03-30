#!/usr/bin/env python3
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

	params_file_path = os.path.join(
		get_package_share_directory("ultrasonic_pkg"),
		'params',
		'ultrasonic_publisher.yaml'
	)
	
	return LaunchDescription([
	
		DeclareLaunchArgument(
			'--params_file',
			default_value=params_file_path,
			description='Path to YAML parameters file'
		),
		
		Node(
			package='ultrasonic_pkg',
			executable='ultrasonic_publisher',
			name='ultrasonic_publisher',
			emulate_tty=True,
			output='screen',
			arguments=[{
				'--params-file': LaunchConfiguration('--params_file'),
			}]
		),
	])
	
	
	
