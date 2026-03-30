#include <iostream>
#include <string>
#include <atomic>
#include <chrono>
#include <cstring>
#include <stdlib.h>
#include <errno.h>
#include <termios.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/range.hpp"
#include "ultrasonic_ros/ultrasonic_usb.hpp"

using namespace std::chrono_literals;

class UltrasonicPublisher : public rclcpp::Node
{
	public:
		UltrasonicPublisher()
		: Node("ultrasonic_publisher")
		{
			auto ret = init_arduino ();
			switch (ret) {
			case -1:
				RCLCPP_INFO(this->get_logger(), "Failed to open.\n");
				break;
			case -2:
				RCLCPP_INFO(this->get_logger(), "Failed to get attributes.\n");
				break;
			case -3:
				RCLCPP_INFO(this->get_logger(), "Failed to configure.\n");
				break;
			default:
				RCLCPP_INFO(this->get_logger(), "Successfully initialized Arduino.\n");
				break;
			}
			
			L_publisher_ = this->create_publisher<sensor_msgs::msg::Range>("L_ultrasonic", 10);
			C_publisher_ = this->create_publisher<sensor_msgs::msg::Range>("C_ultrasonic", 10);
			R_publisher_ = this->create_publisher<sensor_msgs::msg::Range>("R_ultrasonic", 10);
			timer_ = this->create_wall_timer(
			500ms, std::bind(&UltrasonicPublisher::timer_callback, this));
		}
		
		uint8_t l_data;
		uint8_t c_data;
		uint8_t r_data;
		
	private:
		void timer_callback()
		{
			get_arduino_data (&l_data, &c_data, &r_data);
			
			RCLCPP_INFO(this->get_logger(), "%d, %d, %d", l_data, c_data, r_data);
			if (l_data < 201) // Max dist. we care about is 200cm
			{
				auto L_message = sensor_msgs::msg::Range();
				L_message.header.stamp = this->get_clock()->now();
				L_message.header.frame_id = "left_ultrasonic_frame";
				L_message.radiation_type = sensor_msgs::msg::Range::ULTRASOUND;
				L_message.field_of_view = 0.1; // Radians, should change based on docs
				L_message.min_range = 0.01; //meters
				L_message.max_range = 2.0;
				L_message.range = ( (float)l_data / 100.0 );
				RCLCPP_INFO(this->get_logger(), " | Left: %f m | ", L_message.range);
				L_publisher_->publish(L_message);
			}
			
			if (c_data < 201) // Max dist. we care about is 200cm
			{
				auto C_message = sensor_msgs::msg::Range();
				C_message.header.stamp = this->get_clock()->now();
				C_message.header.frame_id = "center_ultrasonic_frame";
				C_message.radiation_type = sensor_msgs::msg::Range::ULTRASOUND;
				C_message.field_of_view = 0.1; // Radians, should change based on docs
				C_message.min_range = 0.01; //meters
				C_message.max_range = 2.0;
				C_message.range = ( (float)c_data / 100.0 );
				RCLCPP_INFO(this->get_logger(), " | Center: %f m| ", C_message.range);
				C_publisher_->publish(C_message);
			}
			
			if (r_data < 201) // Max dist. we care about is 200cm
			{
				auto R_message = sensor_msgs::msg::Range();
				R_message.header.stamp = this->get_clock()->now();
				R_message.header.frame_id = "right_ultrasonic_frame";
				R_message.radiation_type = sensor_msgs::msg::Range::ULTRASOUND;
				R_message.field_of_view = 0.1; // Radians, should change based on docs
				R_message.min_range = 0.01; //meters
				R_message.max_range = 2.0;
				R_message.range = ( (float)r_data / 100.0 );
				RCLCPP_INFO(this->get_logger(), " | Right: %f m | ", R_message.range);
				R_publisher_->publish(R_message);
			}
			
		}
		rclcpp::TimerBase::SharedPtr timer_;
		rclcpp::Publisher<sensor_msgs::msg::Range>::SharedPtr L_publisher_;
		rclcpp::Publisher<sensor_msgs::msg::Range>::SharedPtr C_publisher_;
		rclcpp::Publisher<sensor_msgs::msg::Range>::SharedPtr R_publisher_;
};


int main(int argc, char * argv[])
{
	rclcpp::init(argc, argv);
	rclcpp::spin(std::make_shared<UltrasonicPublisher>());
	rclcpp::shutdown();
	return 0;
}









