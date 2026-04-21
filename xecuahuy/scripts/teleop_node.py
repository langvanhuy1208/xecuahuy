#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray
import sys, termios, tty, threading, time

msg = """
=====================================
  ĐIỀU KHIỂN ROBOT XECUAHUY (TOGGLE MODE)
=====================================
DI CHUYỂN (Ấn 1 lần là chạy mãi):
      w (Tiến)          u : Nâng lên
  a   s   d             j : Hạ xuống
      x (Lùi)           h : Xoay Trái
                        k : Xoay Phải

TỐC ĐỘ:
  + : Tăng | - : Giảm

DỪNG:
  s hoặc Space : DỪNG KHẨN CẤP
  q : Thoát
=====================================
"""

class TeleopXecuahuy(Node):
    def __init__(self):
        super().__init__('teleop_node')

        self.pub_wheel = self.create_publisher(Twist, '/diff_drive_controller/cmd_vel_unstamped', 10)
        self.pub_arm   = self.create_publisher(Float64MultiArray, '/arm_controller/commands', 10)
        
        self.settings = termios.tcgetattr(sys.stdin)

        # Trạng thái di chuyển
        self.linear_val = 0.0
        self.angular_val = 0.0
        self.speed = 0.5
        self.arm_pos = [0.0, 0.0]
        self.done = False

        # Thread gửi lệnh liên tục (Heartbeat) - Đây là phần quan trọng nhất
        self.heartbeat_thread = threading.Thread(target=self.publish_loop)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()

    def publish_loop(self):
        """Gửi lệnh đi mỗi 0.05s (20Hz) bất kể có bấm phím hay không"""
        while rclpy.ok() and not self.done:
            # Gửi lệnh bánh xe
            twist = Twist()
            twist.linear.x = self.linear_val
            twist.angular.z = self.angular_val
            self.pub_wheel.publish(twist)

            # Gửi lệnh tay máy
            arm_msg = Float64MultiArray()
            arm_msg.data = self.arm_pos
            self.pub_arm.publish(arm_msg)
            
            time.sleep(0.05) 

    def getKey(self):
        tty.setraw(sys.stdin.fileno())
        # Đọc 1 ký tự, không chờ enter
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def run(self):
        print(msg)
        try:
            while not self.done:
                key = self.getKey()

                # Điều hướng - Chỉ gán giá trị 1 lần
                if key == 'w':
                    self.linear_val = self.speed
                    self.angular_val = 0.0
                elif key == 'x':
                    self.linear_val = -self.speed
                    self.angular_val = 0.0
                elif key == 'a':
                    self.linear_val = 0.0
                    self.angular_val = self.speed * 2.0
                elif key == 'd':
                    self.linear_val = 0.0
                    self.angular_val = -self.speed * 2.0
                elif key in ('s', ' '):
                    self.linear_val = 0.0
                    self.angular_val = 0.0
                
                # Tốc độ
                elif key == '+':
                    self.speed = min(self.speed + 0.1, 2.0)
                elif key == '-':
                    self.speed = max(self.speed - 0.1, 0.1)

                # Tay máy
                elif key == 'u': self.arm_pos[0] = min(0.0, self.arm_pos[0] + 0.005)
                elif key == 'j': self.arm_pos[0] = max(-0.04, self.arm_pos[0] - 0.005)
                elif key == 'h': self.arm_pos[1] = min(1.57, self.arm_pos[1] + 0.1)
                elif key == 'k': self.arm_pos[1] = max(-1.57, self.arm_pos[1] - 0.1)

                elif key == 'q':
                    self.done = True
                
                print(f"\rLệnh: {key} | V: {self.linear_val:.2f} | W: {self.angular_val:.2f} | Arm: {self.arm_pos}    ", end="")

        except Exception as e:
            print(f"\nLỗi: {e}")
        finally:
            self.stop_robot()

    def stop_robot(self):
        self.done = True
        self.linear_val = 0.0
        self.angular_val = 0.0
        self.pub_wheel.publish(Twist())
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)

def main():
    rclpy.init()
    node = TeleopXecuahuy()
    node.run()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
