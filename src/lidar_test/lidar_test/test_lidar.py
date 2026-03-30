# ~/ros2_ws/src/lidar_test/lidar_test/test_lidar.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import numpy as np
import math

class LidarProcessor(Node):
    def __init__(self):
        super().__init__('lidar_processor')

        # Declare params 
        self.declare_parameter('crop_angle_min', 0.0)
        self.declare_parameter('crop_angle_max', 6.2831)    
        self.declare_parameter('crop_distance_min', 0.11999)
        self.declare_parameter('crop_distance_max', 3.5)

        #get params
        self.crop_angle_min = self.get_parameter('crop_angle_min').get_parameter_value().double_value
        self.crop_angle_max = self.get_parameter('crop_angle_max').get_parameter_value().double_value
        self.crop_distance_min = self.get_parameter('crop_distance_min').get_parameter_value().double_value
        self.crop_distance_max = self.get_parameter('crop_distance_max').get_parameter_value().double_value


        
        # subscribe to the scan topic (topic type: sensor_msgs/LaserScan)
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',  
            self.scan_callback,
            10)  # queue size
        
        # publisher to publish cropped scans ( scans facing a specific direction )
        self.publisher = self.create_publisher(LaserScan, '/cropped_scan', 10)
        
        self.get_logger().info('LidarProcessor node started, listening to /scan')
        
        # Statistics
        self.scan_count = 0
        self.min_distance = float('inf')
        self.max_distance = 0.0
        
    def scan_callback(self, msg):

        # create cropped scan message ( have to initialize all fields even if we re not using them)
        cropped_scan = LaserScan()
        cropped_scan.header = msg.header
        cropped_scan.angle_min = msg.angle_min
        cropped_scan.angle_max = msg.angle_max
        cropped_scan.angle_increment = msg.angle_increment
        cropped_scan.time_increment = msg.time_increment
        cropped_scan.scan_time = msg.scan_time
        cropped_scan.range_min = msg.range_min
        cropped_scan.range_max = msg.range_max

        cropped_ranges = []     # to hold cropped ranges

        # Increment scan count
        self.scan_count += 1
        
        # convert ranges to numpy array for processing
        ranges = np.array(msg.ranges)
        
        # filter out obnoxious values
        valid_ranges = ranges[np.isfinite(ranges)]
        
        if len(valid_ranges) > 0:
            # calculate statistics
            current_min = np.min(valid_ranges)
            current_max = np.max(valid_ranges)
            current_avg = np.mean(valid_ranges)
            
            # update overall stats
            self.min_distance = min(self.min_distance, current_min)
            self.max_distance = max(self.max_distance, current_max)
            
            # log every 10th scan
            if self.scan_count % 10 == 0:
                self.get_logger().info(
                    f'Scan #{self.scan_count}: '
                    f'{len(valid_ranges)}/{len(ranges)} valid measurements\n'
                    f'  Current: min={current_min:.2f}m, max={current_max:.2f}m, avg={current_avg:.2f}m\n'
                    f'  Overall: min={self.min_distance:.2f}m, max={self.max_distance:.2f}m'
                )
                
                # detect close obstacles
                close_obstacles = valid_ranges[valid_ranges < 0.5]  # Within 0.5m
                if len(close_obstacles) > 0:
                    self.get_logger().warning(
                        f'{len(close_obstacles)} close obstacle(s) detected (< 0.5m)'
                    )
                    
        else:
            self.get_logger().warn('No valid distance measurements in this scan')

        # Crop the scan based on angle and distance
        for i in range(len(msg.ranges)):
            angle = msg.angle_min + i * msg.angle_increment
            # convert angle
            angle_normalized = self.convert_angle(angle)
            # check if angles and distance in bounds
            if (self.crop_angle_min <= angle_normalized <= self.crop_angle_max and
                self.crop_distance_min <= msg.ranges[i] <= self.crop_distance_max):
                cropped_ranges.append(msg.ranges[i])
            else:
                cropped_ranges.append(float('inf'))

        cropped_scan.ranges = cropped_ranges

        #publish cropped scan
        self.publisher.publish(cropped_scan)

    # Function to convert angle to 0 to 2pi
    def convert_angle(self, angle):
        if angle < 0:
            return angle + 2 * math.pi
        else:
            return angle



def main(args=None):
    rclpy.init(args=args)
    node = LidarProcessor()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting off republisher node.')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()