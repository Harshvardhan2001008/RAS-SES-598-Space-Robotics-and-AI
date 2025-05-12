#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import cv2


class RGBDSyncWithIntrinsics(Node):
    def __init__(self):
        super().__init__('rgbd_sync_with_intrinsics')
        self.bridge = CvBridge()

        # Publishers
        self.rgb_info_pub = self.create_publisher(CameraInfo, '/rgb_camera/camera_info', 10)
        self.depth_info_pub = self.create_publisher(CameraInfo, '/depth_camera/camera_info', 10)
        self.rgb_sync_pub = self.create_publisher(Image, '/synced/rgb_camera', 10)
        self.depth_sync_pub = self.create_publisher(Image, '/synced/depth_camera', 10)
        self.rgb_info_sync_pub = self.create_publisher(CameraInfo, '/synced/rgb_camera/camera_info', 10)
        self.depth_info_sync_pub = self.create_publisher(CameraInfo, '/synced/depth_camera/camera_info', 10)

        # Subscribers
        self.rgb_sub = self.create_subscription(Image, '/rgb_camera', self.rgb_cb, 10)
        self.depth_sub = self.create_subscription(Image, '/depth_camera', self.depth_cb, 10)

        # Camera intrinsics for 640x480 (example values)
        fx = fy = 554.256
        cx, cy = 320.0, 240.0
        width, height = 640, 480

        # CameraInfo (shared)
        self.rgb_info = CameraInfo()
        self.rgb_info.header.frame_id = 'camera_link'
        self.rgb_info.width = width
        self.rgb_info.height = height
        self.rgb_info.k = [fx, 0.0, cx, 0.0, fy, cy, 0.0, 0.0, 1.0]
        self.rgb_info.d = [0.0] * 5
        self.rgb_info.r = [1.0, 0.0, 0.0,
                           0.0, 1.0, 0.0,
                           0.0, 0.0, 1.0]
        self.rgb_info.p = [fx, 0.0, cx, 0.0,
                           0.0, fy, cy, 0.0,
                           0.0, 0.0, 1.0, 0.0]

        self.depth_info = CameraInfo()
        self.depth_info.header.frame_id = 'camera_link'
        self.depth_info.width = width
        self.depth_info.height = height
        self.depth_info.k = self.rgb_info.k
        self.depth_info.d = self.rgb_info.d
        self.depth_info.r = self.rgb_info.r
        self.depth_info.p = self.rgb_info.p

        # Intrinsics publishing timer
        self.timer = self.create_timer(0.5, self.publish_intrinsics)

        self.last_rgb = None
        self.last_depth = None

    def publish_intrinsics(self):
        now = self.get_clock().now().to_msg()
        self.rgb_info.header.stamp = now
        self.depth_info.header.stamp = now
        self.rgb_info_pub.publish(self.rgb_info)
        self.depth_info_pub.publish(self.depth_info)

    def rgb_cb(self, msg):
        try:
            cv_rgb = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')
            resized_rgb = cv2.resize(cv_rgb, (640, 480))
            resized_msg = self.bridge.cv2_to_imgmsg(resized_rgb, encoding='rgb8')
            #resized_msg.header = msg.header
            # Force the frame_id to 'camera_link'
            resized_msg.header.frame_id = 'camera_link'
            resized_msg.header.stamp = msg.header.stamp
            self.last_rgb = resized_msg
        except Exception as e:
            self.get_logger().error(f"RGB resize failed: {e}")
        self.try_publish()

    def depth_cb(self, msg):
        try:
            cv_depth = self.bridge.imgmsg_to_cv2(msg, desired_encoding='32FC1')
            resized_depth = cv2.resize(cv_depth, (640, 480))
            resized_msg = self.bridge.cv2_to_imgmsg(resized_depth, encoding='32FC1')
            #resized_msg.header = msg.header
            # Force the frame_id to 'camera_link'
            resized_msg.header.frame_id = 'camera_link'
            resized_msg.header.stamp = msg.header.stamp
            self.last_depth = resized_msg
        except Exception as e:
            self.get_logger().error(f"Depth resize failed: {e}")
        self.try_publish()

    def try_publish(self):
        if self.last_rgb and self.last_depth:
            now = self.get_clock().now().to_msg()
            for msg in [self.last_rgb, self.last_depth, self.rgb_info, self.depth_info]:
                msg.header.stamp = now

            self.rgb_sync_pub.publish(self.last_rgb)
            self.depth_sync_pub.publish(self.last_depth)
            self.rgb_info_sync_pub.publish(self.rgb_info)
            self.depth_info_sync_pub.publish(self.depth_info)

            self.get_logger().info("✅ Published synced & resized RGB, Depth, and CameraInfo")
            self.last_rgb = None
            self.last_depth = None


def main(args=None):
    rclpy.init(args=args)
    node = RGBDSyncWithIntrinsics()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

