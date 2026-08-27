from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    share = FindPackageShare('fast_livo2')
    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true'),
        Node(package='fast_livo2', executable='fastlivo_mapping', name='laserMapping',
             output='screen', parameters=[PathJoinSubstitution([share, 'config', 'HILTI22.yaml']),
                                          PathJoinSubstitution([share, 'config', 'camera_fisheye_HILTI22.yaml'])]),
        Node(package='rviz2', executable='rviz2', name='rviz', output='screen',
             arguments=['-d', PathJoinSubstitution([share, 'rviz_cfg', 'hilti.rviz'])],
             condition=IfCondition(LaunchConfiguration('rviz'))),
    ])
