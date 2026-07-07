#!/usr/bin/env python3
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range
from geometry_msgs.msg import Twist


class UltrasonicEstop(Node):
    """Independent safety failsafe.

    LIDAR-based Nav2 costmap obstacle avoidance is the primary obstacle
    detection system. This node is a last-resort backstop for the LIDAR's
    blind spots (e.g. low obstacles below the scan plane): it zeroes the
    robot's velocity via twist_mux's highest-priority input whenever any
    ultrasonic sensor reads closer than min_safe_distance, and simply stops
    publishing once every sensor is clear again so lower-priority commands
    (Nav2, joystick) resume through twist_mux.
    """

    def __init__(self):
        super().__init__('ultrasonic_estop')

        self.declare_parameter('frame_ids', [
            'left_ultrasonic', 'center_ultrasonic', 'right_ultrasonic'])
        self.declare_parameter('min_safe_distance', 0.15)  # meters
        self.declare_parameter('max_reading_age', 1.0)     # seconds
        self.declare_parameter('publish_rate', 10.0)       # Hz

        self.frame_ids = self.get_parameter('frame_ids').value
        self.min_safe_distance = self.get_parameter('min_safe_distance').value
        self.max_reading_age = self.get_parameter('max_reading_age').value
        publish_rate = self.get_parameter('publish_rate').value

        self._latest_range = {}
        self._latest_stamp = {}

        for frame_id in self.frame_ids:
            topic = f'range/{frame_id}'
            self.create_subscription(
                Range, topic,
                lambda msg, fid=frame_id: self._range_callback(msg, fid),
                10)

        self._estop_pub = self.create_publisher(Twist, 'cmd_vel_estop', 10)
        self._timer = self.create_timer(1.0 / publish_rate, self._check_and_publish)

        self.get_logger().info(
            f'Ultrasonic e-stop watching {self.frame_ids} '
            f'at {self.min_safe_distance:.2f} m')

    def _range_callback(self, msg: Range, frame_id: str):
        self._latest_range[frame_id] = msg.range
        self._latest_stamp[frame_id] = time.monotonic()

    def _check_and_publish(self):
        now = time.monotonic()
        unsafe = False
        for frame_id in self.frame_ids:
            stamp = self._latest_stamp.get(frame_id)
            if stamp is None or (now - stamp) > self.max_reading_age:
                continue  # no recent reading from this sensor
            if self._latest_range[frame_id] < self.min_safe_distance:
                unsafe = True
                break

        if unsafe:
            self._estop_pub.publish(Twist())  # all-zero


def main(args=None):
    rclpy.init(args=args)
    node = UltrasonicEstop()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
