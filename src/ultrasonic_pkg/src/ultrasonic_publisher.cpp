#include <iostream>
#include <string>
#include <atomic>
#include <chrono>
#include <cstring>
#include <vector>
#include <map>
#include <functional>
#include <stdlib.h>
#include <errno.h>
#include <termios.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/range.hpp>
#include "ultrasonic_pkg/ultrasonic_usb.hpp"
#include "ultrasonic_pkg/ultrasonic_publisher.hpp"

#define LEFT 	0
#define CENTER 	1
#define RIGHT	2

// CLASS INIT / DESTROY ******************************************
UltrasonicPublisher::UltrasonicPublisher(const rclcpp::NodeOptions & options)
: Node("ultrasonic_publisher", options)
{		
	declare_parameters();
	
	param_callback_handler_ = this->add_on_set_parameters_callback(
		std::bind(&UltrasonicPublisher::on_parameter_change, this, std::placeholders::_1)
	);
	
	for (size_t i = 0; i < frame_ids_.size(); i++)
	{
		std::string topic = "range/" + frame_ids_[i];
		auto publisher = this->create_publisher<sensor_msgs::msg::Range>(topic, 10);
		
		publishers_.push_back(publisher);
		RCLCPP_INFO(this->get_logger(), "Created publisher for %s on topic %s",
			frame_ids_[i].c_str(), topic.c_str()
		);
	}
	
	sensor_data_.resize(frame_ids_.size());
	sensor_msgs_.resize(frame_ids_.size());
	
	if (!initialize_sensors())
	{
		RCLCPP_ERROR(this->get_logger(), 
			"Failed to initialize ultrasonic sensors."
		);
		return;
	}
	
	int period_ms = static_cast<int>(1000.0 / update_rate_);
	timer_ = this->create_wall_timer(
		std::chrono::milliseconds(period_ms),
		std::bind(&UltrasonicPublisher::timer_callback, this)
	);
	
	RCLCPP_INFO(this->get_logger(), "Ultrasonic Publisher initialized with %zu sensors at %.1f Hz",
		frame_ids_.size(), update_rate_
	);
}

UltrasonicPublisher::~UltrasonicPublisher()
{
	RCLCPP_INFO(this->get_logger(), "Ultrasonic publisher shutting down...");
}

bool 
UltrasonicPublisher::initialize_sensors()
{
	auto ret = init_arduino();
	switch (ret)
	{
	case -1:
		RCLCPP_ERROR(this->get_logger(), "Failed to open.\n");
		break;
	case -2:
		RCLCPP_ERROR(this->get_logger(), "Failed to get attributes.\n");
		break;
	case -3:
		RCLCPP_ERROR(this->get_logger(), "Failed to configure.\n");
		break;
	default:
		RCLCPP_INFO(this->get_logger(), "Successfully initialized Arduino.\n");
		break;
	}
	
	if (ret < 0) { return false; }
	
	for (size_t i = 0; i < frame_ids_.size(); i++)
	{
		auto message = sensor_msgs::msg::Range();
		message.radiation_type = sensor_msgs::msg::Range::ULTRASOUND;
		message.field_of_view = field_of_view_;
		message.min_range = min_range_;
		message.max_range = max_range_;
		message.header.frame_id = frame_ids_[i];
		sensor_msgs_.push_back(message);
	}
	
	return true;
}

// CLASS PARAMETERS ******************************************
void
UltrasonicPublisher::declare_parameters()
{
	this->declare_parameter<std::vector<std::string>>("frame_ids",
		std::vector<std::string>{
			"left_ultrasonic", 
			"center_ultrasonic", 
			"right_ultrasonic"
		}
	);
	
	this->declare_parameter<double>("update_rate", 20.0); // Hz
	this->declare_parameter<double>("field_of_view", 0.5236); // ~30 degrees
	this->declare_parameter<double>("min_range", 0.02); // meters
	this->declare_parameter<double>("max_range", 2.0); // meters
	this->declare_parameter<bool>("publish_tf", false);
	
	frame_ids_ = this->get_parameter("frame_ids").as_string_array();
	
	if (frame_ids_.empty())
	{
		RCLCPP_WARN(this->get_logger(),
			"No frame IDs provided, using defaults"
		);
		
		frame_ids_ = {
			"left_ultrasonic", 
			"center_ultrasonic",
			"right_ultrasonic"
		};
	}
	
	update_rate_ = this->get_parameter("update_rate").as_double();
	field_of_view_ = this->get_parameter("field_of_view").as_double();
	min_range_ = this->get_parameter("min_range").as_double();
	max_range_ = this->get_parameter("max_range").as_double();
	publish_tf_ = this->get_parameter("publish_tf").as_bool();
}

rcl_interfaces::msg::SetParametersResult
UltrasonicPublisher::on_parameter_change(const std::vector<rclcpp::Parameter> & parameters)
{
	rcl_interfaces::msg::SetParametersResult result;
	result.successful = true;
	
	for (const auto & param : parameters)
	{
		if (param.get_name() == "frame_ids")
		{
			if (param.get_type() == rclcpp::ParameterType::PARAMETER_STRING_ARRAY)
			{
				auto new_frame_ids = param.as_string_array();
				if (new_frame_ids.size() == frame_ids_.size())
				{
					frame_ids_ = new_frame_ids;
					RCLCPP_INFO(this->get_logger(),
						"Updated frame IDs.\n"
					);
				}
				else
				{
					RCLCPP_WARN(this->get_logger(),
						"Cannot change number of sensors dynamically.\n"
					);
					result.successful = false;
				}
			}
		}
		else if (param.get_name() == "update_rate")
		{
			update_rate_ = param.as_double();
			// Reset timer
			int period_ms = static_cast<int>(1000.0 / update_rate_);
			timer_ = this->create_wall_timer(
				std::chrono::milliseconds(period_ms),
				std::bind(&UltrasonicPublisher::timer_callback, this)
			);
		}
		else if (param.get_name() == "field_of_view")
		{
			auto new_field_of_view = param.as_double();
			if (new_field_of_view > 0 && new_field_of_view < 3.141)
			{
				field_of_view_ = new_field_of_view;
				RCLCPP_INFO(this->get_logger(),
					"Updated field of view.\n"
				);
			}
			else
			{
				RCLCPP_WARN(this->get_logger(),
					"FoV of %lf radians is not possible.\n",
					new_field_of_view
				);
				result.successful = false;
			}
		}
		else if (param.get_name() == "min_range")
		{
			auto new_min = param.as_double();
			if (new_min > 0.0 && new_min < max_range_)
			{
				min_range_ = new_min;
				RCLCPP_INFO(this->get_logger(),
					"Update minimum range."
				);
			}
			else
			{
				RCLCPP_WARN(this->get_logger(),
					"Minimum range of %lf is not possible.\n",
					new_min
				);
				result.successful = false;
			}
		}
		else if (param.get_name() == "max_range")
		{
			auto new_max = param.as_double();
			if (new_max > 0.0 && new_max > min_range_)
			{
				max_range_ = new_max;
				RCLCPP_INFO(this->get_logger(),
					"Update maximum range."
				);
			}
			else
			{
				RCLCPP_WARN(this->get_logger(),
					"Maximum range of %lf is not possible.\n",
					new_max
				);
				result.successful = false;
			}
		}
		else if (param.get_name() == "publish_tf")
		{
			publish_tf_ = param.as_bool();
			RCLCPP_INFO(this->get_logger(),
				"Updated `publish_tf` boolean.\n"
			);
		}
		else
		{
			RCLCPP_WARN(this->get_logger(),
				"Unrecognized parameter.\n"
			);
		}			
	}
	
	return result;
}
			
void
UltrasonicPublisher::publish_data()
{
	auto now = this->get_clock()->now();
	
	for (size_t i = 0; i < publishers_.size(); i++)
	{
		sensor_msgs_[i].header.stamp = now;
		if (sensor_data_[i] <= 200)
		{
			sensor_msgs_[i].range = sensor_data_[i];
			publishers_[i]->publish(sensor_msgs_[i]);
			RCLCPP_INFO(this->get_logger(),
				"Published %s: range=%f\n",
				frame_ids_[i].c_str(), sensor_msgs_[i].range
			);
		}
		else
		{
			RCLCPP_INFO(this->get_logger(),
				"Invalid data from %s\n",
				frame_ids_[i].c_str()
			);
		}
	}
}

		
void
UltrasonicPublisher::timer_callback()
{
	get_arduino_data(&sensor_data_[LEFT], &sensor_data_[CENTER], &sensor_data_[RIGHT]);	
	publish_data();
}
		



int 
main (int argc, char * argv[])
{
	rclcpp::init(argc, argv);
	rclcpp::spin(std::make_shared<UltrasonicPublisher>());
	rclcpp::shutdown();
	return 0;
}





