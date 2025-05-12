#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
from ultralytics import YOLO
from visualization_msgs.msg import Marker
from geometry_msgs.msg import PointStamped
from tf2_ros import Buffer, TransformListener, TransformException
from tf2_geometry_msgs import do_transform_point
import cv2
import numpy as np
import os
import csv

class RockLocator(Node):
    def __init__(self):
        super().__init__('rock_locator')
        self.bridge = CvBridge()
        self.model = YOLO('/home/harsh/ros2_project/src/ros2_project/ros2_project/ros2_project/best.pt')

        self.rgb_sub = self.create_subscription(Image, '/synced/rgb_camera', self.image_callback, 10)
        self.caminfo_sub = self.create_subscription(CameraInfo, '/synced/rgb_camera/camera_info', self.caminfo_callback, 10)
        self.depth_sub = self.create_subscription(Image, '/synced/depth_camera', self.depth_callback, 10)

        self.marker_pub = self.create_publisher(Marker, '/rock_marker', 10)
        self.image_pub = self.create_publisher(Image, '/final_image', 10)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.camera_info = None
        self.latest_depth = None

        log_path = os.path.expanduser('~/rock_detections_log.csv')
        self.csv_file = open(log_path, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['timestamp', 'label', 'confidence', 'x', 'y', 'z'])
        self.get_logger().info(f"📄 Logging rock detections to: {log_path}")

    def caminfo_callback(self, msg):
        self.camera_info = msg

    def depth_callback(self, msg):
        self.latest_depth = msg

    def image_callback(self, msg):
        if self.camera_info is None :
            self.get_logger().warn("Waiting for camera info and depth image...")
            return

        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        if self.latest_depth is None:
            self.get_logger().warn("No depth image, skipping world coordinate calculation for detection {i}.")
            continue

        depth_image = self.bridge.imgmsg_to_cv2(self.latest_depth, desired_encoding='passthrough')
        Z = float(depth_image[v, u])
            if Z == 0.0 or np.isnan(Z):
                self.get_logger().warn(f"Invalid depth at ({u}, {v})")
                continue

            X = (u - cx) * Z / fx
            Y = (v - cy) * Z / fy

            point_cam = PointStamped()
            point_cam.header.frame_id = self.camera_info.header.frame_id
            point_cam.header.stamp = msg.header.stamp
            point_cam.point.x = X
            point_cam.point.y = Y
            point_cam.point.z = Z

            try:
                transform = self.tf_buffer.lookup_transform(
                    'world', point_cam.header.frame_id,
                    rclpy.time.Time.from_msg(point_cam.header.stamp),
                    timeout=rclpy.duration.Duration(seconds=0.2)
                )
            except TransformException as e:
                self.get_logger().warn(f"Transform failed, trying latest: {e}")
                try:
                    transform = self.tf_buffer.lookup_transform(
                        'world', point_cam.header.frame_id,
                        rclpy.time.Time(),
                        timeout=rclpy.duration.Duration(seconds=0.2)
                    )
                except TransformException as e2:
                    self.get_logger().warn(f"TF lookup failed: {e2}")
                    continue

            try:
                point_world = do_transform_point(point_cam, transform)
            except Exception as e:
                self.get_logger().warn(f"Transform error: {e}")
                continue

            marker = Marker()
            marker.header.frame_id = 'world'
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.type = Marker.SPHERE
            marker.pose.position = point_world.point
            marker.scale.x = marker.scale.y = marker.scale.z = 0.3
            marker.color.r = 1.0
            marker.color.g = 0.3
            marker.color.b = 0.2
            marker.color.a = 1.0
            marker.id = i
            self.marker_pub.publish(marker)

            timestamp = point_cam.header.stamp.sec + point_cam.header.stamp.nanosec * 1e-9
            self.csv_writer.writerow([
                f"{timestamp:.6f}",
                label_name,
                f"{conf:.2f}",
                f"{point_world.point.x:.3f}",
                f"{point_world.point.y:.3f}",
                f"{point_world.point.z:.3f}"
            ])
            self.get_logger().info(f"[Rock {i}] {label_name}: {conf:.2f} @ "
                                   f"({point_world.point.x:.2f}, {point_world.point.y:.2f}, {point_world.point.z:.2f})")

        annotated_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding='bgr8')
        annotated_msg.header = msg.header
        self.image_pub.publish(annotated_msg)

    def destroy_node(self):
        self.csv_file.close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = RockLocator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

