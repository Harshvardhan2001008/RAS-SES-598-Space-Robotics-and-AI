#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from px4_msgs.msg import VehicleOdometry
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

class OdometryTFBroadcaster(Node):
    def __init__(self):
        super().__init__('odometry_tf_broadcaster')

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=10
        )

        self.subscription = self.create_subscription(
            VehicleOdometry,
            '/fmu/out/vehicle_odometry',
            self.listener_callback,
            qos_profile)

        self.br = TransformBroadcaster(self)
        self.get_logger().info("✅ odometry_tf_broadcaster started with BEST_EFFORT QoS")

    def listener_callback(self, msg):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = 'base_link'

    # Explicitly cast to Python float
        t.transform.translation.x = float(msg.position[0])
        t.transform.translation.y = float(msg.position[1])
        t.transform.translation.z = float(msg.position[2])
        t.transform.rotation.x = float(msg.q[0])
        t.transform.rotation.y = float(msg.q[1])
        t.transform.rotation.z = float(msg.q[2])
        t.transform.rotation.w = float(msg.q[3])

        self.br.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = OdometryTFBroadcaster()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

