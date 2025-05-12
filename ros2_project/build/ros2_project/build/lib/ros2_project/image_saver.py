#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
import sys
import termios
import tty
import select
import threading

class ImageSaver(Node):
    def __init__(self):
        super().__init__('image_saver')
        self.bridge = CvBridge()
        self.latest_msg = None
        self.counter = 0
        self.save_path = os.path.expanduser('~/ros2_project/image_data')
        os.makedirs(self.save_path, exist_ok=True)

        self.subscription = self.create_subscription(
            Image,
            '/rgb_camera',
            self.listener_callback,
            10)
        
        self.get_logger().info("📸 Press SPACE to save an image, 'q' to quit, or Ctrl+C to interrupt")
        self.key_thread = threading.Thread(target=self.key_listener, daemon=True)
        self.key_thread.start()

    def listener_callback(self, msg):
        self.latest_msg = msg

    def save_image(self):
        if self.latest_msg is None:
            self.get_logger().warn("⚠️ No image received yet.")
            return
        try:
            cv_image = self.bridge.imgmsg_to_cv2(self.latest_msg, desired_encoding='passthrough')
            filename = os.path.join(self.save_path, f'image_{self.counter:03d}.png')
            cv2.imwrite(filename, cv_image)
            self.get_logger().info(f'✅ Saved image: {filename}')
            self.counter += 1
        except Exception as e:
            self.get_logger().error(f'❌ Failed to save image: {e}')

    def getch(self, timeout=0.1):
        """Non-blocking single character input with timeout."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            if select.select([sys.stdin], [], [], timeout)[0]:
                return sys.stdin.read(1)
            return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def key_listener(self):
        while rclpy.ok():
            key = self.getch()
            if key == ' ':
                self.save_image()
            elif key == 'q':
                self.get_logger().info("🛑 Quit key pressed. Shutting down...")
                rclpy.shutdown()
                break

def main(args=None):
    rclpy.init(args=args)
    node = ImageSaver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("🛑 Ctrl+C detected. Shutting down...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

