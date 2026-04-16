import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    bringup_dir = get_package_share_directory('bring_up')
    
    ekf_config = os.path.join(bringup_dir, 'config', 'ekf_navsat_params.yaml')
    
    return LaunchDescription([
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node_odom',
            output='screen',
            parameters=[ekf_config],
            remappings=[('/odometry/filtered', '/odometry/local')]
        ),
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node_map',
            output='screen',
            parameters=[ekf_config],
            remappings=[('/odometry/filtered', '/odometry/global')]
        ),
        Node(
            package='robot_localization',
            executable='navsat_transform_node',
            name='navsat_transform',
            output='screen',
            parameters=[ekf_config],
            remappings=[
                ('/gps/fix', '/gps/robot/fix'),
                ('/odometry/filtered', '/odometry/global')
            ]
        )
    ])