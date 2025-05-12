#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO
from visualization_msgs.msg import MarkerArray, Marker
import cv2
import numpy as np
import sys
print(f"🧠 Running Python from: {sys.executable}")

class RockDetector(Node):
    def __init__(self):
        super().__init__('rock_detector')
        self.bridge = CvBridge()
        self.model = YOLO('/home/harsh/ros2_project/src/ros2_project/ros2_project/ros2_project/best.pt')
        self.subscriber = self.create_subscription(
            Image,
            '/rgb_camera',
            self.image_callback,
            10
        )
        self.image_pub = self.create_publisher(Image, '/yolo_annotated', 10)

    def image_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        results = self.model(cv_image)

        names = self.model.names  # class index to name mapping

        boxes = results[0].boxes
        for i in range(len(boxes)):
            x1, y1, x2, y2 = map(int, boxes.xyxy[i].tolist())
            cls_id = int(boxes.cls[i].item()) if boxes.cls is not None else -1
            conf = float(boxes.conf[i].item()) if boxes.conf is not None else 0.0

            label = f'{self.model.names[cls_id]}: {conf:.2f}' if cls_id in self.model.names else f'ID {cls_id}: {conf:.2f}'

    # Draw box
            cv2.rectangle(cv_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Draw label background
            (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1, 5)
            cv2.rectangle(cv_image, (x1, y1 - text_height - baseline), (x1 + text_width, y1), (0, 255, 0), -1)
            cv2.putText(cv_image, label, (x1, y1 - baseline), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)


        annotated_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding='bgr8')
        annotated_msg.header = msg.header
        self.image_pub.publish(annotated_msg)


def main(args=None):
    rclpy.init(args=args)
    node = RockDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

