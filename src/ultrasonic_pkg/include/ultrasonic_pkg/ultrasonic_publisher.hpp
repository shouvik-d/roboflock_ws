#ifndef ULTRASONIC_PUBLISHER_HPP
#define ULTRASONIC_PUBLISHER_HPP

#include <vector>
#include <string>
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/range.hpp>

class UltrasonicPublisher : public rclcpp::Node
{
	public:
		explicit UltrasonicPublisher(const rclcpp::NodeOptions & options = rclcpp::NodeOptions());
		~UltrasonicPublisher();
		
	private:
		void declare_parameters();
		rcl_interfaces::msg::SetParametersResult on_parameter_change(const std::vector<rclcpp::Parameter> & parameters);
		bool initialize_sensors();
		void publish_data();
		void timer_callback();
		
		// Publisher Variables
		rclcpp::TimerBase::SharedPtr timer_;	std::vector<rclcpp::Publisher<sensor_msgs::msg::Range>::SharedPtr> publishers_;
		std::vector<uint8_t> sensor_data_;
		std::vector<sensor_msgs::msg::Range> sensor_msgs_;
		
		// Parameters
		rclcpp::node_interfaces::OnSetParametersCallbackHandle::SharedPtr param_callback_handler_;
		std::vector<std::string> frame_ids_;
		double update_rate_;
		double field_of_view_;
		double min_range_;
		double max_range_;
		bool publish_tf_;
};

#endif /* ULTRASONIC_PUBLISHER_HPP */
