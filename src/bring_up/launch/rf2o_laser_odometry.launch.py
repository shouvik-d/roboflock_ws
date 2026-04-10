import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    bringup_dir = get_package_share_directory('bring_up')
    
    rf2o_config = os.path.join(bringup_dir, 'config', 'rf2o_config.yaml')
    
    return LaunchDescription([

        Node(
            package='rf2o_laser_odometry', 
            executable='rf2o_laser_odometry_node', 
            name='rf2o_laser_odometry',
            output='screen',
            parameters=[rf2o_config]
    )  
        ])