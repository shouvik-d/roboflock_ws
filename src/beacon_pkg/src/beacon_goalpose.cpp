#include <cmath>

#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/nav_sat_fix.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <robot_localization/srv/from_ll.hpp>
#include <tf2/exceptions.h>
#include <tf2_ros/buffer.h>
#include <tf2_ros/transform_listener.h>

using FromLL = robot_localization::srv::FromLL;

// Converts the beacon's GPS fix into a Nav2 /goal_pose. The conversion goes
// through navsat_transform_node's /fromLL service instead of doing its own
// lat/lon -> UTM math, because that service already holds the rover's real
// datum (its own first GPS fix, per ekf_navsat_params.yaml's
// wait_for_datum: false) - the only origin that is actually consistent with
// Nav2's live map frame. Computing our own origin from the beacon's first
// fix (the old approach) produced a goal in a frame unrelated to the map
// Nav2 is actually navigating in.
class BeaconGoalPose : public rclcpp::Node
{
public:
  BeaconGoalPose() : Node("beacon_goalpose")
  {
    declare_parameter<double>("min_goal_update_distance", 0.4);
    min_goal_update_distance_ = get_parameter("min_goal_update_distance").as_double();

    tf_buffer_ = std::make_shared<tf2_ros::Buffer>(this->get_clock());
    tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);

    from_ll_client_ = create_client<FromLL>("/fromLL");

    publisher_ = create_publisher<geometry_msgs::msg::PoseStamped>("/goal_pose", 10);

    // from nmea_serial_driver, relayed to the rover over the HC-12 link
    subscriber_ = create_subscription<sensor_msgs::msg::NavSatFix>(
      "/gps/beacon/fix",
      rclcpp::QoS(10),
      std::bind(&BeaconGoalPose::gpsCallback, this, std::placeholders::_1));

    has_last_goal_ = false;
  }

private:
  void gpsCallback(const sensor_msgs::msg::NavSatFix::SharedPtr msg)
  {
    if (!from_ll_client_->service_is_ready()) {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 5000,
        "Waiting for /fromLL service (navsat_transform_node not up yet)...");
      return;
    }

    auto request = std::make_shared<FromLL::Request>();
    request->ll_point.latitude = msg->latitude;
    request->ll_point.longitude = msg->longitude;
    request->ll_point.altitude = msg->altitude;

    from_ll_client_->async_send_request(
      request,
      std::bind(&BeaconGoalPose::fromLLResponseCallback, this, std::placeholders::_1));
  }

  void fromLLResponseCallback(rclcpp::Client<FromLL>::SharedFuture future)
  {
    auto response = future.get();
    double x = response->map_point.x;
    double y = response->map_point.y;

    if (has_last_goal_) {
      double dx = x - last_goal_x_;
      double dy = y - last_goal_y_;
      if (std::hypot(dx, dy) < min_goal_update_distance_) {
        // Beacon hasn't moved far enough to justify a new goal/replan -
        // debounces raw GPS jitter so Nav2 isn't constantly re-planning.
        return;
      }
    }

    geometry_msgs::msg::PoseStamped goal_pose;
    goal_pose.header.stamp = now();
    goal_pose.header.frame_id = "map";
    goal_pose.pose.position.x = x;
    goal_pose.pose.position.y = y;
    goal_pose.pose.position.z = 0.0;

    double yaw = 0.0;
    try {
      auto robot_tf = tf_buffer_->lookupTransform("map", "base_link", tf2::TimePointZero);
      yaw = std::atan2(
        y - robot_tf.transform.translation.y,
        x - robot_tf.transform.translation.x);
    } catch (const tf2::TransformException & ex) {
      RCLCPP_WARN(
        get_logger(),
        "Could not look up map->base_link (%s); publishing goal with identity orientation",
        ex.what());
    }

    goal_pose.pose.orientation.z = std::sin(yaw / 2.0);
    goal_pose.pose.orientation.w = std::cos(yaw / 2.0);

    publisher_->publish(goal_pose);

    last_goal_x_ = x;
    last_goal_y_ = y;
    has_last_goal_ = true;
  }

  double min_goal_update_distance_;
  bool has_last_goal_;
  double last_goal_x_ = 0.0;
  double last_goal_y_ = 0.0;

  std::shared_ptr<tf2_ros::Buffer> tf_buffer_;
  std::shared_ptr<tf2_ros::TransformListener> tf_listener_;
  rclcpp::Client<FromLL>::SharedPtr from_ll_client_;
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
