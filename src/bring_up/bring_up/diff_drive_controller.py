import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import odrive
from odrive.enums import AxisState, InputMode, ControlMode
import math

WHEEL_RADIUS = 0.254
WHEEL_SEPARATION = 0.3
GEAR_RATIO = 30.0
SERIAL_NUMBERS = {
    "FR": "316633543334",
    "FL": "357B358B3135",
    "RR": "336636543334",
    "RL": "336536573334",
}

FAST_DECEL = 50.0
STD_ACCEL  = 10.0

class DiffDriveController(Node):
    def __init__(self):
        super().__init__('diff_drive_controller')
        self.drives = {}
        self._connect_and_enable()
        self.create_subscription(Twist, 'cmd_vel', self._cmd_vel_cb, 10)
        self.get_logger().info('Diff drive controller ready, listening on /cmd_vel')

    def _connect_and_enable(self):
        for name, serial in SERIAL_NUMBERS.items():
            self.get_logger().info(f'Connecting to {name} ({serial})...')
            dev = odrive.find_sync(serial_number=serial)
            dev.clear_errors()
            dev.axis0.controller.config.input_mode = InputMode.VEL_RAMP
            dev.axis0.controller.config.vel_ramp_rate = STD_ACCEL
            dev.axis0.controller.config.vel_integrator_gain = 0.0  # was 0.05
            dev.axis0.controller.config.vel_gain = 0.1
            dev.axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL
            self.drives[name] = dev
            self.get_logger().info(f'{name} connected and enabled')

    def _set_velocity(self, name: str, target_vel: float):
        dev = self.drives[name]
        current_vel = dev.axis0.encoder.vel_estimate

        slowing_down = abs(target_vel) < abs(current_vel)
        changing_dir = target_vel * current_vel < 0

        if slowing_down or changing_dir:
            dev.axis0.controller.config.vel_ramp_rate = FAST_DECEL
        else:
            dev.axis0.controller.config.vel_ramp_rate = STD_ACCEL

        dev.axis0.controller.input_vel = target_vel

    def _cmd_vel_cb(self, msg: Twist):
        v = msg.linear.x
        w = msg.angular.z
        print(f"cmd_vel → linear: {v}, angular: {w}")

        v_left  = v - (w * WHEEL_SEPARATION / 2.0)
        v_right = v + (w * WHEEL_SEPARATION / 2.0)
        print(f"v_left: {v_left} m/s, v_right: {v_right} m/s")

        turns_left  = (v_left  / (2.0 * math.pi * WHEEL_RADIUS)) * GEAR_RATIO
        turns_right = (v_right / (2.0 * math.pi * WHEEL_RADIUS)) * GEAR_RATIO

        self._set_velocity("FL",  turns_left)
        self._set_velocity("RL",  turns_left)
        self._set_velocity("FR", -turns_right)
        self._set_velocity("RR", -turns_right)

    def destroy_node(self):
        self.get_logger().info('Shutting down — stopping and idling motors')
        for dev in self.drives.values():
            dev.axis0.controller.input_vel = 0.0
            dev.axis0.requested_state = AxisState.IDLE
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = DiffDriveController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
