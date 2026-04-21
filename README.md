# Tạo cấu trúc thư mục workspace
mkdir -p ~/xecuahuy_ws/src

# Sao chép mã nguồn từ thư mục Downloads vào workspace
cp -r ~/Downloads/xecuahuy ~/xecuahuy_ws/src/

# Cài đặt các thành phần phụ thuộc (Dependencies)
cd ~/xecuahuy_ws
rosdep update
rosdep install --from-paths src --ignore-src -r -y

# Biên dịch và Khởi chạy mô phỏng Gazebo
killall -9 gzserver gzclient
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:~/xecuahuy_ws/src
cd ~/xecuahuy_ws
colcon build --packages-select xecuahuy
source install/setup.bash
ros2 launch xecuahuy full_system.launch.py

# Chạy nút điều khiển bằng bàn phím (Teleop)
cd ~/xecuahuy_ws
source install/setup.bash
ros2 run xecuahuy teleop_node.py
