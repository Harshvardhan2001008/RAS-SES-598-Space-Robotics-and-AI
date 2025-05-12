#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
from ultralytics import YOLO
from visualization_msgs.msg import Marker
from geometry_msgs.msg import PointStamped
from tf2_ros import Buffer, TransformListener
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
        self.depth_sub = self.create_subscription(Image, '/synced/depth_camera', self.depth_callback, 10)
        self.caminfo_sub = self.create_subscription(CameraInfo, '/synced/rgb_camera/camera_info', self.caminfo_callback, 10)

        self.marker_pub = self.create_publisher(Marker, '/rock_marker', 10)
        self.image_pub = self.create_publisher(Image, '/final_image', 10)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.camera_info = None
        self.latest_depth = None

        # Setup CSV logging
        log_path = os.path.expanduser('~/rock_detections_log.csv')
        self.csv_file = open(log_path, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['timestamp', 'label', 'confidence', 'x', 'y', 'z'])  # header

        self.get_logger().info(f"📄 Logging rock detections to: {log_path}")

    def caminfo_callback(self, msg):
        self.camera_info = msg

    def depth_callback(self, msg):
        self.latest_depth = msg

    def image_callback(self, msg):
        if self.camera_info is None or self.latest_depth is None:
            self.get_logger().warn("Waiting for camera info and depth image...")
            return

        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        depth_image = self.bridge.imgmsg_to_cv2(self.latest_depth, desired_encoding='passthrough')

        # 1. Extract camera intrinsic parameters
        fx = self.camera_info.k[0]
        fy = self.camera_info.k[4]
        cx = self.camera_info.k[2]
        cy = self.camera_info.k[5]

        # 2. Run YOLOv8 inference
        results = self.model(cv_image)

        annotated_frame = cv_image.copy() # For visualization

        for i, det in enumerate(results.xyxy[0]):  # Iterate through detected objects
            if len(det) >= 6:
                x_min, y_min, x_max, y_max, conf, cls = det.cpu().numpy()
                label_int = int(cls)
                label_name = self.model.names[label_int]

                # Assuming you are only interested in 'rock' class (adjust if needed)
                if label_name == 'rock':
                    center_u = int((x_min + x_max) / 2)
                    center_v = int((y_min + y_max) / 2)

                    # 3. Get depth at the center of the detected rock
                    if 0 <= center_v < depth_image.shape[0] and 0 <= center_u < depth_image.shape[1]:
                        Z = float(depth_image[center_v, center_u])
                        if not np.isnan(Z) and Z > 0.0:
                            # 4. Calculate 3D point in camera frame
                            X = (center_u - cx) * Z / fx
                            Y = (center_v - cy) * Z / fy

                            point_cam = PointStamped()
                            point_cam.header.frame_id = self.camera_info.header.frame_id
                            point_cam.header.stamp = msg.header.stamp
                            point_cam.point.x = X
                            point_cam.point.y = Y
                            point_cam.point.z = Z

                            # 5. Transform to world frame
                            try:
                                transform = self.tf_buffer.lookup_transform(
                                    'world', point_cam.header.frame_id,
                                    rclpy.time.Time.from_msg(point_cam.header.stamp),
                                    timeout=rclpy.duration.Duration(seconds=0.1)
                                )
                                point_world = do_transform_point(point_cam, transform)

                                # 6. Publish marker
                                marker = Marker()
                                marker.header.frame_id = 'world'
                                marker.header.stamp = self.get_clock().now().to_msg()
                                marker.type = Marker.SPHERE
                                marker.pose.position = point_world.point
                                marker.scale.x = marker.scale.y = marker.scale.z = 0.2  # Adjust scale
                                marker.color.r = 1.0
                                marker.color.g = 0.3
                                marker.color.b = 0.2
                                marker.color.a = 1.0
                                marker.id = i
                                self.marker_pub.publish(marker)

                                # 7. Log detection
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

                            except TransformException as e:
                                self.get_logger().warn(f"Transform failed: {e}")

                    # Draw bounding boxes on the image for visualization
                    pt1 = (int(x_min), int(y_min))
                    pt2 = (int(x_max), int(y_max))
                    cv2.rectangle(annotated_frame, pt1, pt2, (0, 255, 0), 2)
                    cv2.putText(annotated_frame, f'{label_name} {conf:.2f}', (pt1[0], pt1[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Publish the annotated image
        annotated_msg = self.bridge.cv2_to_imgmsg(annotated_frame, encoding='bgr8')
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

