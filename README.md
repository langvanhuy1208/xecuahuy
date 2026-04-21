# xecuahuy
# Tạo workspace & thêm package

cd ~ && mkdir -p xecuahuy/src && cp -r ~/Downloads/xecuahuy ~/xecuahuy_ws/src/
Cài dependency

cd ~/xecuahuy_ws && rosdep install --from-paths src --ignore-src -r -y

# chay gazebo

killall -9 gzserver gzclient;
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:~/xecuahuy_ws/src;
cd ~/xecuahuy_ws;
colcon build --packages-select xecuahuy;
source install/setup.bash;
ros2 launch xecuahuy full_system.launch.py

# chay teleop_nope
cd ~/xecuahuy_ws && source install/setup.bash && ros2 run xecuahuy teleop_node.py
