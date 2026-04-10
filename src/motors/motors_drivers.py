import odrive
from odrive.enums import AxisState
import time

class RobotDrive:
    def _init_(self):
        self.serial_numbers_hex = {
            "FR": "316633543334", # CONFIGURED
            "FL": "357B358B3135", # CONFIGURED
            "RR": "336636543334", # CONFIGURED
            "RL": "336536573334" # CONFIGURED 
        }
        self.drives = {}

    def connect(self):
        print("Connecting to all ODrives...")
        for name, serial in self.serial_numbers_hex.items():
            print(f"  Connecting to {name} ({serial})...")
            self.drives[name] = odrive.find_sync(serial_number=serial)
            print(f"  {name} connected!")
        print("All ODrives connected.")

    def enable_all(self):
        print("Enabling closed loop control...")
        for name, dev in self.drives.items():
            # Clear any phantom errors from booting up
            dev.clear_errors()
            # Immediately enter closed loop (no calibration needed)
            dev.axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL

        time.sleep(0.5)

        for name, dev in self.drives.items():
            state = dev.axis0.current_state
            if state == AxisState.CLOSED_LOOP_CONTROL:
                print(f"  {name} enabled ✓")
            else:
                print(f"  {name} FAILED — axis_err: {dev.axis0.error} | motor_err: {dev.axis0.motor.error}")

    def set_velocity(self, fl=0.0, fr=0.0, rl=0.0, rr=0.0):
        """Set velocity in turns/sec."""
        self.drives["FL"].axis0.controller.input_vel = fl
        self.drives["FR"].axis0.controller.input_vel = fr
        self.drives["RL"].axis0.controller.input_vel = rl
        self.drives["RR"].axis0.controller.input_vel = rr

    def set_rpm(self, fl=0.0, fr=0.0, rl=0.0, rr=0.0):
        """Set velocity in RPM — converts automatically."""
        self.set_velocity(fl / 60, fr / 60, rl / 60, rr / 60)

    def stop(self):
        print("Stopping all motors...")
        self.set_velocity(0, 0, 0, 0)

    def idle_all(self):
        print("Setting all motors to idle...")
        for name, dev in self.drives.items():
            dev.axis0.requested_state = AxisState.IDLE
            print(f"  {name} idle")

    def check_errors(self):
        print("Checking errors...")
        for name, dev in self.drives.items():
            print(f"  {name} -> Axis: {dev.axis0.error} | Motor: {dev.axis0.motor.error} | Encoder: {dev.axis0.encoder.error}")

# --- Usage ---
if _name_ == "_main_":
    robot = RobotDrive()
    robot.connect()
    robot.check_errors()
    robot.enable_all()

    print("Running motors...")
    # Note: 1000 RPM / 60 = 16.6 turns/sec
    robot.set_rpm(fl=2500, fr=2500, rl=2500, rr=2500)

    time.sleep(10)

    robot.stop()
    robot.idle_all()