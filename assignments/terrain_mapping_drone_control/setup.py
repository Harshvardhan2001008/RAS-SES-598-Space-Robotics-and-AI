from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'terrain_mapping_drone_control'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch',
            glob('launch/*.launch.py')),
        ('share/' + package_name + '/config',
            glob('config/*')),
        ('share/' + package_name + '/models/terrain',
            glob('models/terrain/*.*')),
        ('share/' + package_name + '/models/terrain/meshes',
            glob('models/terrain/meshes/*.*')),
        ('share/' + package_name + '/models/cylinder',
            glob('models/cylinder/*.*')),
        ('share/' + package_name + '/models/cylinder/materials',
            glob('models/cylinder/materials/*.*')),
        ('share/' + package_name + '/models/cylinder_small',
            glob('models/cylinder_small/*.*')),
        ('share/' + package_name + '/models/cylinder_small/materials',
            glob('models/cylinder_small/materials/*.*')),
        ('share/' + package_name + '/models/cylinder_small/materials/textures',
            glob('models/cylinder_small/materials/textures/*.*')),
        ('lib/' + package_name, [
            'terrain_mapping_drone_control/cylinder_landing_node.py',
            'terrain_mapping_drone_control/aruco_tracker.py',
            'terrain_mapping_drone_control/aruco_landing.py',
            'terrain_mapping_drone_control/takeoff_and_hover.py',
            'terrain_mapping_drone_control/dimension_estimator.py',
            'terrain_mapping_drone_control/energy_logger.py',
            'terrain_mapping_drone_control/spiral_trajectory.py'
        ]),
        ('share/' + package_name + '/models/cylinder_short',
            glob('models/cylinder_short/*.*')),
        ('share/' + package_name + '/models/cylinder_short/materials',
            glob('models/cylinder_short/materials/*.*')),
        ('share/' + package_name + '/models/cylinder_short/materials/textures',
            glob('models/cylinder_short/materials/textures/*.*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='A ROS2 package for executing spiral trajectory with PX4',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'cylinder_landing_node = terrain_mapping_drone_control.cylinder_landing_node:main',
            'px4_odom_converter = terrain_mapping_drone_control.px4_odom_converter:main',
            'feature_tracker = terrain_mapping_drone_control.feature_tracker:main',
            'pose_visualizer = terrain_mapping_drone_control.pose_visualizer:main',
            'camera_info_publisher = terrain_mapping_drone_control.camera_info_publisher:main',
            'spiral_trajectory = terrain_mapping_drone_control.spiral_trajectory:main',
            'aruco_tracker = terrain_mapping_drone_control.aruco_tracker:main',
            'aruco_landing = terrain_mapping_drone_control.aruco_landing:main',
            'aruco_landing_controller = terrain_mapping_drone_control.aruco_landing_controller:main',
            'takeoff_and_hover = terrain_mapping_drone_control.takeoff_and_hover:main',
            'dimension_estimator = terrain_mapping_drone_control.dimension_estimator:main',
            'energy_logger = terrain_mapping_drone_control.energy_logger:main',
        ],
    },
    python_requires='>=3.8'
) 
