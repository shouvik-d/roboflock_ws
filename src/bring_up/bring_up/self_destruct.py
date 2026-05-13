#!/usr/bin/env python3
"""
Custom Teleop Node for ROS 2  –  verified controller mappings
=============================================================
CONTROLS:
  R1  (btn 6)       Dead-man switch – hold for any movement
  R2  (axis 5)      Drive forward   at current linear speed  (binary, any press)
  L2  (axis 4)      Drive backward  at current linear speed  (binary, any press)
  Right stick X     Turn left / right  (axis 3: left=+1, right=-1)
  D-pad Up / Down   Increase / decrease linear  speed  (axis 7: up=+1, dn=-1)
  D-pad Rt / Left   Increase / decrease angular speed  (axis 6: lt=+1, rt=-1)
  PS  (btn ?)       Run BASH_SCRIPT  <- verify BTN_PS index then remove this note
"""

import subprocess
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist

# -- Confirmed mappings --------------------------------------------------------
BTN_R1         = 5    # R1 dead-man switch 

AXIS_R2        = 4    # R2 trigger: rest=+1.0, fully pressed=-1.0  (was 4 = right stick Y)
AXIS_L2        = 3    # L2 trigger: rest=+1.0, fully pressed=-1.0  (was 3 = right stick X)
TRIGGER_THRESH = -0.5

AXIS_STEER     = 2    # right stick X: left=+1.0, right=-1.0 
AXIS_DPAD_Y    = 7     # linear 
AXIS_DPAD_X    = 6      #angular 

BTN_PS         = 12   #bash
# -----------------------------------------------------------------------------

# -- Path to your script ------------------------------------------------------
BASH_SCRIPT = '/home/roboflock/roboflock_ws/src/bring_up/bring_up/bring_up.sh'   # <-- set your path here
# -----------------------------------------------------------------------------

# Speed limits
LINEAR_MIN,  LINEAR_MAX  = 0.5, 10.0
ANGULAR_MIN, ANGULAR_MAX = 0.5, 10.0
SPEED_STEP = 0.5
STEER_DEADZONE = 0.1

class PS4Teleop(Node):
    def __init__(self):
        super().__init__('ps4_teleop')

        self.linear_speed  = 0.5   # m/s   – forward / backward fixed speed
        self.angular_speed = 0.5   # rad/s – right stick scale

        # Edge-detection state
        self._prev_dpad_x = 0.0
        self._prev_dpad_y = 0.0
        self._prev_ps     = 0


        # change cmd_vel to cmd_vel_joy for nav2
        self._cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.create_subscription(Joy, 'joy', self._joy_cb, 10)

        self.get_logger().info(
            f'Teleop ready  |  linear={self.linear_speed:.2f} m/s  '
            f'angular={self.angular_speed:.2f} rad/s'
        )

    # -- Main callback ---------------------------------------------------------
    def _joy_cb(self, msg: Joy) -> None:
        self._handle_speed_adjust(msg)
        self._handle_ps_button(msg)
        self._publish_velocity(msg)

    # -- Velocity command ------------------------------------------------------
    def _publish_velocity(self, msg: Joy) -> None:
        twist = Twist()

        if msg.buttons[BTN_R1]:                          # dead-man held

            r2_pressed = msg.axes[AXIS_R2] < TRIGGER_THRESH
            l2_pressed = msg.axes[AXIS_L2] < TRIGGER_THRESH

            if r2_pressed:
                twist.linear.x = self.linear_speed      # forward
            elif l2_pressed:
                twist.linear.x = -self.linear_speed     # backward

            # Right stick left=+1 -> turn left = positive angular.z
            steer = msg.axes[AXIS_STEER]
            if abs(steer) < STEER_DEADZONE:
                steer = 0.0
            twist.angular.z = steer * self.angular_speed
        self._cmd_pub.publish(twist)

    # -- D-pad speed adjustment (edge-triggered, ignores held) -----------------
    def _handle_speed_adjust(self, msg: Joy) -> None:
        dpad_y = msg.axes[AXIS_DPAD_Y]
        dpad_x = msg.axes[AXIS_DPAD_X]

        # Linear speed: d-pad Up(+1) = increase, Down(-1) = decrease
        if dpad_y != self._prev_dpad_y:
            if dpad_y > 0.5:
                self.linear_speed = round(
                    min(LINEAR_MAX, self.linear_speed + SPEED_STEP), 2)
                self.get_logger().info(f'Linear  speed -> {self.linear_speed:.2f} m/s')
            elif dpad_y < -0.5:
                self.linear_speed = round(
                    max(LINEAR_MIN, self.linear_speed - SPEED_STEP), 2)
                self.get_logger().info(f'Linear  speed -> {self.linear_speed:.2f} m/s')
            self._prev_dpad_y = dpad_y

        # Angular speed: d-pad Right(-1) = increase, Left(+1) = decrease
        if dpad_x != self._prev_dpad_x:
            if dpad_x < -0.5:                           # right arrow
                self.angular_speed = round(
                    min(ANGULAR_MAX, self.angular_speed + SPEED_STEP), 2)
                self.get_logger().info(f'Angular speed -> {self.angular_speed:.2f} rad/s')
            elif dpad_x > 0.5:                          # left arrow
                self.angular_speed = round(
                    max(ANGULAR_MIN, self.angular_speed - SPEED_STEP), 2)
                self.get_logger().info(f'Angular speed -> {self.angular_speed:.2f} rad/s')
            self._prev_dpad_x = dpad_x

    # -- PS button -> run script (fires once on press, not while held) ----------
    def _handle_ps_button(self, msg: Joy) -> None:
        ps = msg.buttons[BTN_PS]
        if ps and not self._prev_ps:
            self.get_logger().info(f'PS button -> launching {BASH_SCRIPT}')
            try:
                subprocess.Popen(['/bin/bash', BASH_SCRIPT])
            except FileNotFoundError:
                self.get_logger().error(f'Script not found: {BASH_SCRIPT}')
        self._prev_ps = ps


def main(args=None):
    rclpy.init(args=args)
    node = PS4Teleop()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
