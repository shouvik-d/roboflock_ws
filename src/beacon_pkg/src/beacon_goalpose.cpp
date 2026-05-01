#include <rclcpp/rclcpp.hpp>
#include "sensor_msgs/msg/nav_sat_fix.hpp"
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geodesy/utm.h>
#include <geodesy/wgs84.h>
#include <geographic_msgs/msg/geo_point.hpp>

class BeaconGoalPose : public rclcpp::Node{

    public:
        BeaconGoalPose(): Node("beacon_goalpose"){

            //from nmea_serial_driver
            subscriber_ = this->create_subscription<sensor_msgs::msg::NavSatFix>("/gps/beacon/fix",
            rclcpp::QoS(10),
            std::bind(&BeaconGoalPose::callback, this, std::placeholders::_1));

            //goal_pose for nav2
            publisher_ = this->create_publisher<geometry_msgs::msg::PoseStamped>("/goal_pose",10);

            //wait for first gps message to set origin
            origin_set_ = false;
        };

    private:
        void callback(const sensor_msgs::msg::NavSatFix::SharedPtr msg){

            geographic_msgs::msg::GeoPoint wgs;
            
            wgs.latitude = msg->latitude;
            wgs.longitude = msg->longitude;
            wgs.altitude = msg->altitude;

            geodesy::UTMPoint utm;
            //convert lat lon to utm
            geodesy::fromMsg(wgs, utm);

            //set origin if not set
            if (!origin_set_){
                origin_.easting = utm.easting;
                origin_.northing = utm.northing;
                origin_.zone = utm.zone;
                origin_.band = utm.band;
                origin_set_ = true;
                return;
            }

            double x = utm.easting - origin_.easting;
            double y = utm.northing - origin_.northing;

            geometry_msgs::msg::PoseStamped goal_pose;
            goal_pose.header.stamp = now();
            goal_pose.header.frame_id = "map";
            goal_pose.pose.position.x = x;
            goal_pose.pose.position.y = y;
            goal_pose.pose.position.z = 0.0;
            
            //not sure about this one and can add more orientation ones if needed
            goal_pose.pose.orientation.w = 1.0;

            publisher_->publish(goal_pose);
        };

    bool origin_set_;
    geodesy::UTMPoint origin_;

    rclcpp::Subscription<sensor_msgs::msg::NavSatFix>::SharedPtr subscriber_;
    rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr publisher_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<BeaconGoalPose>());
  rclcpp::shutdown();
  return 0;
}