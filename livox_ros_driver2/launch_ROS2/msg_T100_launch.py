import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node

xfer_format = 1
multi_topic = 0
data_src = 0
publish_freq = 10.0
output_type = 0
frame_id = 'livox_frame'
lvx_file_path = '/home/livox/livox_test.lvx'
cmdline_bd_code = 'livox0000000001'

cur_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../config')
user_config_path = os.path.join(cur_config_path, 'T100_config.json')

livox_ros2_params = [
    {'xfer_format': xfer_format}, {'multi_topic': multi_topic},
    {'data_src': data_src}, {'publish_freq': publish_freq},
    {'output_data_type': output_type}, {'frame_id': frame_id},
    {'lvx_file_path': lvx_file_path}, {'user_config_path': user_config_path},
    {'cmdline_input_bd_code': cmdline_bd_code},
]


def generate_launch_description():
    sampling_command = ExecuteProcess(
        cmd=['python3', os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     'send_t100_sampling.py')],
        name='t100_sampling_command', output='screen')
    driver = Node(
        package='livox_ros_driver2', executable='livox_ros_driver2_node',
        name='livox_t100_publisher', output='screen', parameters=livox_ros2_params)
    return LaunchDescription([
        sampling_command,
        RegisterEventHandler(OnProcessExit(
            target_action=sampling_command, on_exit=[driver]))
    ])
