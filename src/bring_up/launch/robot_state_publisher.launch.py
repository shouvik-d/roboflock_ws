from launch import LaunchDescription
from launch_ros.actions import Node
import os
import xacro
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    
    file = os.path.join(
    get_package_share_directory('urdf_description'),
    'urdf',
    'URDF.xacro'
)

    robot_description_config = xacro.process_file(file)
    robot_description = robot_description_config.toxml()

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description
            }]
        )
    ])