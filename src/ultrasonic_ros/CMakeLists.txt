cmake_minimum_required(VERSION 3.8)
project(ultrasonic_ros)

if(NOT CMAKE_CXX_STANDARD)
	set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()


find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)

include_directories(
	include/${PROJECT_NAME}/
)

set(LIB_HEADER_FILES
	include/${PROJECT_NAME}/ultrasonic_usb.hpp
)

set(LIB_SOURCE_FILES
	src/ultrasonic_usb.cpp
)

foreach(src_file ${LIB_SOURCE_FILES})
	if(NOT EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/${src_file})
		message(WARNING "Source file not found: ${src_file}")
	else()
		message(STATUS "Found source file: ${src_file}")
	endif()
endforeach()

add_library(${PROJECT_NAME}_lib ${LIB_SOURCE_FILES} ${LIB_HEADER_FILES})

target_include_directories(${PROJECT_NAME}_lib PUBLIC
	"$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
	"$<INSTALL_INTERFACE:include/${PROJECT_NAME}>"
)

target_link_libraries(${PROJECT_NAME}_lib PUBLIC
	${rclcpp_LIBRARIES}
	${std_msgs_LIBRARIES}
	${sensor_msgs_LIBRARIES}
)

install(DIRECTORY include/${PROJECT_NAME}
	DESTINATION include
)

install(TARGETS ${PROJECT_NAME}_lib
	LIBRARY DESTINATION lib
	ARCHIVE DESTINATION lib
	RUNTIME DESTINATION bin
	INCLUDES DESTINATION include/${PROJECT_NAME}
)

ament_export_include_directories(include)
ament_export_libraries(${PROJECT_NAME}_lib)
ament_export_dependencies(rclcpp std_msgs sensor_msgs)

add_executable(ultrasonic_publisher src/ultrasonic_publisher.cpp)

target_include_directories(ultrasonic_publisher PRIVATE
	"<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
	"$<INSTALL_INTERFACE:include/${PROJECT_NAME}>"
)

target_link_libraries(ultrasonic_publisher 
	${PROJECT_NAME}_lib
	rclcpp::rclcpp
	${std_msgs_TARGETS}
	${sensor_msgs_TARGETS}
)

install(TARGETS ultrasonic_publisher
	DESTINATION lib/${PROJECT_NAME}
)

ament_package()
