#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import math
from px4_msgs.msg import VehicleOdometry
from rclpy.qos import QoSProfile, QoSReliabilityPolicy

class EnergyLogger(Node):
    def __init__(self):
        super().__init__('energy_logger')

        # Use Best Effort QoS to match PX4 publisher
        qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            depth=10
        )

        # Subscribe to vehicle odometry
        self.vehicle_odometry_sub = self.create_subscription(
            VehicleOdometry,
            '/fmu/out/vehicle_odometry',
            self.odometry_callback,
            qos_profile
        )

        self.prev_position = None
        self.total_distance = 0.0

        # Log every 5 seconds
        self.timer = self.create_timer(5.0, self.timer_callback)

        self.get_logger().info('✅ Energy Logger Node Started')

    def odometry_callback(self, msg):
        current_position = (msg.position[0], msg.position[1], msg.position[2])

        if self.prev_position is not None:
            dx = current_position[0] - self.prev_position[0]
            dy = current_position[1] - self.prev_position[1]
            dz = current_position[2] - self.prev_position[2]
            step_distance = math.sqrt(dx**2 + dy**2 + dz**2)

            self.total_distance += step_distance

        self.prev_position = current_position

    def timer_callback(self):
        energy_estimate = self.total_distance  # Assuming 1 unit energy per meter
        self.get_logger().info(
            f"📊 Total Distance Traveled: {self.total_distance:.2f} meters | ⚡ Estimated Energy: {energy_estimate:.2f} units"
        )

def main(args=None):
    rclpy.init(args=args)
    node = EnergyLogger()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

