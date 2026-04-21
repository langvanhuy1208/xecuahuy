cmake_minimum_required(VERSION 3.8)
project(xecuahuy)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(robot_state_publisher REQUIRED)
find_package(gazebo_ros REQUIRED)
find_package(gazebo_ros2_control REQUIRED)
find_package(ros2_control REQUIRED)
find_package(ros2_controllers REQUIRED)

# ĐÃ THÊM "scripts" VÀO ĐÂY ĐỂ NÓ COPY TOÀN BỘ FILE PYTHON VÀO ĐÚNG CHỖ
install(DIRECTORY launch urdf meshes config rviz scripts
  DESTINATION share/${PROJECT_NAME}
)

# Cài đặt file điều khiển trong thư mục scripts (vào thư mục lib cho ROS 2 Node)
install(PROGRAMS
  scripts/teleop_node.py
  scripts/balancing_node.py
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY meshes
  DESTINATION share/${PROJECT_NAME}
)

ament_export_dependencies(robot_state_publisher)
ament_package()
