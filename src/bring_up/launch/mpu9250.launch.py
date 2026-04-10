import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    bringup_dir = get_package_share_directory('bring_up')
    
    mpu9250_config = os.path.join(bringup_dir, 'config', 'mpu9250.yaml')
    
    return LaunchDescription([

        Node(
            package='mpu9250driver', 
            executable='mpu9250driver', 
            name='imu',
            output='screen',
            parameters=[mpu9250_config],
            remappings=[('sensor_msgs/Imu', '/imu/data')]
    )
        ])