import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    bringup_dir = get_package_share_directory('bring_up')
    
    rplidar_config = os.path.join(bringup_dir, 'config', 'rplidar.yaml')
    
    return LaunchDescription([

        Node(
                package='rplidar_ros', 
                executable='rplidar_node', 
                name='rplidar',
                output='screen',
                parameters=[rplidar_config],
        )
        ])