import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import odrive
from odrive.enums import AxisState
import math


WHEEL_RADIUS = 0.254       # meters 
WHEEL_SEPARATION = 0.3  # meters — update to your measured value
GEAR_RATIO = 30.0        # 30:1 gearbox

SERIAL_NUMBERS = {
    "FR": "316633543334",
    "FL": "357B358B3135",
    "RR": "336636543334",
    "RL": "336536573334",
}


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
            dev.axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL
            self.drives[name] = dev
            self.get_logger().info(f'{name} connected and enabled')

    def _cmd_vel_cb(self, msg: Twist):
        v = msg.linear.x
        w = msg.angular.z
        print("Received cmd_vel:")
        print("linear velocity (v): ", v)
        print("angular velocity (w): ", w)
        #testing 
    
        # Diff drive kinematics: v_left/right in m/s
        #try finding the rpm and then convert it to m/s ? 
        v_left  = v - (w * WHEEL_SEPARATION / 2.0)
        v_right = v + (w * WHEEL_SEPARATION / 2.0)
        print("printing v_left and v_right in m/s for debugging")
        print("v_left: ", v_left)
        print("v_right: ", v_right)


        

        # Convert m/s -> motor turns/sec (accounting for gear ratio)
        turns_left  = (v_left  / (2.0 * math.pi * WHEEL_RADIUS)) * GEAR_RATIO
        turns_right = (v_right / (2.0 * math.pi * WHEEL_RADIUS)) * GEAR_RATIO

        # damp right wheels when turning right ( pivot turn) , and left wheels when turning left
        if v > 0 : # turning right
            turns_right = turns_right * 0.0
            turns_left = turns_left * 1.5
            print("dampening right wheels")
            
        #else turn left
        if v < 0 : # turning left
                turns_left = turns_left * 0.0
                turns_right = turns_right * 1.5
                print("dampening left wheels")


        # Left wheels are negated to match physical mounting orientation
        self.drives["FL"].axis0.controller.input_vel =  turns_left
        self.drives["RL"].axis0.controller.input_vel =  turns_left
        self.drives["FR"].axis0.controller.input_vel =  turns_right
        self.drives["RR"].axis0.controller.input_vel =  turns_right

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