# save as image_viewer.py and run with: ros2 run <your_package> image_viewer
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge

class ImageViewer(Node):
    def __init__(self):
        super().__init__('image_viewer')
        self.sub = self.create_subscription(Image, '/rgb_camera/image_raw', self.callback, 10)
        self.bridge = CvBridge()

    def callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        cv2.imshow("Camera", frame)
        cv2.waitKey(1)

rclpy.init()
node = ImageViewer()
rclpy.spin(node)

