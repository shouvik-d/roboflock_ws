import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    bringup_dir = get_package_share_directory('bring_up')
    
    nav2_params_file = os.path.join(bringup_dir, 'config', 'nav2_params.yaml')
    
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            get_package_share_directory('nav2_bringup'), '/launch', '/bringup_launch.py'
        ]),
        launch_arguments={
            'params_file': nav2_params_file,
            'autostart': LaunchConfiguration('autostart')
        }.items()
    )
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'autostart',
            default_value='true',
            description='Automatically start the navigation stack'
        ),
        nav2_bringup_launch
    ])