#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_share = get_package_share_directory('terrain_mapping_drone_control')
    gz_model_path = os.path.join(pkg_share, 'models')

    # Set Gazebo environment variables
    os.environ['PX4_GZ_MODEL_POSE'] = "0,14.5,6.5,0,0,0"
    os.environ['PX4_GZ_WORLD'] = 'custom_world'

    px4_autopilot_path = LaunchConfiguration('px4_autopilot_path')

    # PX4 SITL: starts immediately
    px4_sitl = ExecuteProcess(
        cmd=['make', 'px4_sitl', 'gz_x500_depth'],
        cwd=px4_autopilot_path,
        output='screen'
    )

    # ros_gz_bridge: delayed slightly
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='bridge',
        parameters=[{'use_sim_time': True}],
        arguments=[
            '/rgb_camera@sensor_msgs/msg/Image[gz.msgs.Image',
            '/rgb_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/depth_camera@sensor_msgs/msg/Image[gz.msgs.Image',
            '/depth_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/depth_camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            '/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/mono_camera@sensor_msgs/msg/Image[gz.msgs.Image',
            '/mono_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        remappings=[
            ('/depth_camera/points', '/drone/front_depth/points'),
            ('/camera_info', '/drone/front_depth/camera_info'),
            ('/mono_camera', '/drone/down_mono'),
            ('/mono_camera/camera_info', '/drone/down_mono/camera_info'),
        ],
        output='screen'
    )
    
    static_tf = Node(
    package='tf2_ros',
    executable='static_transform_publisher',
    name='static_tf_pub',
    arguments=['0', '0', '0', '0', '0', '0', 'world', 'camera_link']
    )

    


    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='True',
            description='Use simulation (Gazebo) clock if true'
        ),
        DeclareLaunchArgument(
            'px4_autopilot_path',
            default_value=os.path.join(os.environ['HOME'], 'PX4-Autopilot'),
            description='Path to PX4-Autopilot directory'
        ),

        px4_sitl,

        TimerAction(period=3.0, actions=[bridge]),
        #TimerAction(period=5.0, actions=[control_node]),
        #TimerAction(period=5.5, actions=[velocity_node]),
    ])

