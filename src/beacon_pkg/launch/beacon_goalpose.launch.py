import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    
    
    return LaunchDescription([

        Node(
            package='beacon_pkg', 
            executable='beacon_goalpose', 
            name='beacon_goalpose',
            output='screen'
    )
        ])