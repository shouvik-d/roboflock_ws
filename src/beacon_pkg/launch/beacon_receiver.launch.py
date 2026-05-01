import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    bringup_dir = get_package_share_directory('bring_up')
    
    config = os.path.join(bringup_dir, 'config', 'beacon_gps.yaml')
    
    return LaunchDescription([

        Node(
            package='nmea_navsat_driver', 
            executable='nmea_serial_driver', 
            name='gps',
            output='screen',
            parameters=[config],
            remappings=[('/fix', '/gps/beacon/fix')]
    )
        ])