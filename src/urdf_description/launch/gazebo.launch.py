<<<<<<< HEAD
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
import os
import xacro
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    share_dir = get_package_share_directory('URDF_description')

    xacro_file = os.path.join(share_dir, 'urdf', 'URDF.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    robot_urdf = robot_description_config.toxml()

=======
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution
import xacro

def generate_launch_description():
    pkg_name = 'URDF_description'
    pkg_share = get_package_share_directory(pkg_name)

    # Process URDF file
    xacro_file = os.path.join(pkg_share, 'urdf', 'URDF.xacro')
    doc = xacro.process_file(xacro_file)
    robot_urdf = doc.toxml()

    # Robot State Publisher
>>>>>>> faa0e8358101bead9ad2591501b71885c5b5ade5
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
<<<<<<< HEAD
        parameters=[
            {'robot_description': robot_urdf}
        ]
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher'
    )

    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gzserver.launch.py'
            ])
        ]),
        launch_arguments={
            'pause': 'true'
        }.items()
    )

    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gzclient.launch.py'
            ])
        ])
    )

    urdf_spawn_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'URDF',
            '-topic', 'robot_description'
=======
        parameters=[{
            'robot_description': robot_urdf,
            'use_sim_time': True
        }],
        output='screen'
    )

    # Launch Gazebo Ignition
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ]),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    # Spawn Robot into Gazebo Ignition
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'my_bot',
            '-topic', 'robot_description',
            '-z', '0.5'
>>>>>>> faa0e8358101bead9ad2591501b71885c5b5ade5
        ],
        output='screen'
    )

<<<<<<< HEAD
    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_node,
        gazebo_server,
        gazebo_client,
        urdf_spawn_node,
=======
    # Bridge between Gazebo topics and ROS topics
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
            '/model/my_bot/odometry@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/model/my_bot/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
        ],
        remappings=[
            ('/model/my_bot/odometry', '/odom'),
            ('/model/my_bot/tf', '/gz_tf'),
        ],
        parameters=[{
            'use_sim_time': True
        }],
        output='screen'
    )

    # TF relay to publish Gazebo TF to ROS TF
    tf_relay = Node(
        package='topic_tools',
        executable='relay',
        name='tf_relay',
        arguments=['/gz_tf', '/tf'],
        output='screen'
    )

    # Joint State Publisher
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{
            'use_sim_time': True
        }]
    )

    # RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        gazebo,
        TimerAction(period=5.0, actions=[robot_state_publisher_node]),
        TimerAction(period=5.0, actions=[joint_state_publisher_node]),
        TimerAction(period=8.0, actions=[spawn_robot]),
        TimerAction(period=10.0, actions=[bridge]),
        tf_relay,
        rviz
>>>>>>> faa0e8358101bead9ad2591501b71885c5b5ade5
    ])
