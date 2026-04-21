#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, JointState
from std_msgs.msg import Float64MultiArray
import math

class HuySelfBalancingNode(Node):
    def __init__(self):
        super().__init__('balancing_node')

        # --- 1. Giao tiếp ROS 2 ---
        # Đọc dữ liệu IMU để lấy góc nghiêng
        self.create_subscription(Imu, '/imu', self.imu_callback, 10)
        # Đọc JointState để lấy vận tốc thực tế từ Encoder bánh xe
        self.create_subscription(JointState, '/joint_states', self.joint_state_callback, 10)
        # Gửi lệnh tốc độ tới Controller
        self.velocity_pub = self.create_publisher(Float64MultiArray, '/forward_velocity_controller/commands', 10)

        # --- 2. Thông số PID Cân bằng (Vòng trong - IMU) ---
        self.kp_bal = 25.0  
        self.ki_bal = 0.8   
        self.kd_bal = 1.5   
        
        # --- 3. Thông số PID Tốc độ (Vòng ngoài - Encoder) ---
        # Giúp xe không bị trôi và giữ vị trí đứng yên
        self.kp_vel = 0.05
        self.ki_vel = 0.01

        # --- 4. Biến trạng thái ---
        self.current_pitch = 0.0
        self.current_wheel_vel = 0.0
        self.target_pitch = 0.0 # Sẽ được cập nhật bởi vòng PID tốc độ
        self.target_velocity = 0.0 # Huy muốn xe đứng yên tại chỗ
        
        self.bal_prev_error = 0.0
        self.bal_integral = 0.0
        self.vel_integral = 0.0
        self.last_time = self.get_clock().now()

    def joint_state_callback(self, msg):
        # Lấy vận tốc trung bình của 2 bánh xe
        if len(msg.velocity) >= 2:
            self.current_wheel_vel = (msg.velocity[0] + msg.velocity[1]) / 2.0

    def imu_callback(self, msg):
        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds / 1e9
        if dt <= 0: return

        # Bước A: Tính Pitch từ Quaternion
        q = msg.orientation
        sinp = 2.0 * (q.w * q.y - q.z * q.x)
        self.current_pitch = math.asin(sinp) if abs(sinp) < 1.0 else math.copysign(math.pi/2, sinp)

        # Bước B: PID Tốc độ (Vòng ngoài) - Điều chỉnh góc nghiêng mục tiêu
        # Nếu xe trôi về trước, ta bắt xe ngả ra sau một chút để hãm lại
        vel_error = self.target_velocity - self.current_wheel_vel
        self.vel_integral += vel_error * dt
        self.target_pitch = - (self.kp_vel * vel_error + self.ki_vel * self.vel_integral)

        # Bước C: PID Cân bằng (Vòng trong)
        bal_error = self.target_pitch - self.current_pitch
        self.bal_integral += bal_error * dt
        bal_derivative = (bal_error - self.bal_prev_error) / dt
        
        output = (self.kp_bal * bal_error) + (self.ki_bal * self.bal_integral) + (self.kd_bal * bal_derivative)

        # Bước D: Giới hạn và gửi lệnh
        output = max(min(output, 20.0), -20.0) # Giới hạn tốc độ motor
        msg_cmd = Float64MultiArray()
        msg_cmd.data = [output, output]
        self.velocity_pub.publish(msg_cmd)

        # Cập nhật biến
        self.bal_prev_error = bal_error
        self.last_time = now

        # Log dữ liệu để Huy quan sát trục Z ~9.27
        if int(now.nanoseconds / 1e8) % 20 == 0:
            self.get_logger().info(f'Pitch: {math.degrees(self.current_pitch):.1f}° | Target: {math.degrees(self.target_pitch):.1f}°')

def main(args=None):
    rclpy.init(args=args)
    node = HuySelfBalancingNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
