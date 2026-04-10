#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
import tf2_ros
import math
import time

class SimulatedMovement(Node):
    def __init__(self):
        super().__init__('simulated_movement')
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        self.timer = self.create_timer(0.1, self.publish_transform)
        
        # Start position
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        
        # Movement parameters (slow circular motion)
        self.radius = 0.2  # 20cm radius circle
        self.angular_speed = 0.1  # radians per second
        self.time = 0.0
        
        self.get_logger().info('Starting simulated movement for SLAM initialization')
        
    def publish_transform(self):
        self.time += 0.1  # increment time
        
        # Circular motion
        self.x = self.radius * math.cos(self.angular_speed * self.time)
        self.y = self.radius * math.sin(self.angular_speed * self.time)
        self.theta = self.angular_speed * self.time
        
        # Create transform from odom to base_link
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0
        
        # Convert angle to quaternion
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = math.sin(self.theta / 2.0)
        t.transform.rotation.w = math.cos(self.theta / 2.0)
        
        self.tf_broadcaster.sendTransform(t)
        
        # Log position occasionally
        if int(self.time * 10) % 50 == 0:
            self.get_logger().info(f'Position: x={self.x:.2f}, y={self.y:.2f}, theta={self.theta:.2f}')

def main(args=None):
    rclpy.init(args=args)
    node = SimulatedMovement()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()