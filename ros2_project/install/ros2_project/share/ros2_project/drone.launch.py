#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    package_dir = get_package_share_directory('ros2_project')

    bridge_node = Node(
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

    static_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_base_to_camera',
        arguments=['0.1', '0', '-0.2', '0', '0', '0', 'base_link', 'camera_link']
    )

    odom_tf_node = Node(
        package='ros2_project',
        executable='odometry_tf_broadcaster',
        name='odometry_tf_broadcaster',
        output='screen'
    )

    return LaunchDescription([
        Node(
            package='ros2_project',
            namespace='ros2_project',
            executable='visualizer',
            name='visualizer'
        ),
        Node(
            package='ros2_project',
            namespace='ros2_project',
            executable='processes',
            name='processes',
            prefix='gnome-terminal --'
        ),
        Node(
            package='ros2_project',
            namespace='ros2_project',
            executable='control',
            name='control',
            prefix='gnome-terminal --'
        ),
        Node(
            package='ros2_project',
            namespace='ros2_project',
            executable='velocity_control',
            name='velocity'
        ),
        TimerAction(period=3.0, actions=[bridge_node]),
        static_tf_node,
        odom_tf_node
    ])

