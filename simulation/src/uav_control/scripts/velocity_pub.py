#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Point

class PIDControllerNode(Node):
    def __init__(self):
        super().__init__('velocity_pub')
        
        # Subscribe to the YOLO Centroid
        self.centroid_sub = self.create_subscription(Point, '/tracking/target_centroid', self.centroid_callback, 10)
        
        # Publish Velocity commands to ArduPilot via MAVROS
        self.vel_pub = self.create_publisher(Twist, '/mavros/setpoint_velocity/cmd_vel_unstamped', 10)
        
        # PID Tuning Parameters (Calculated during simulation)
        self.kp_yaw = 0.005
        self.kp_pitch = 0.0001
        
        # Camera Resolution Constants (Assumes 640x480)
        self.center_x = 320.0
        self.target_area = 20000.0 # Desired bounding box size (distance)

        self.get_logger().info("PID Velocity Controller Initialized.")

    def centroid_callback(self, msg):
        cmd = Twist()
        
        # 1. YAW PID: Keep target centered horizontally
        error_x = self.center_x - msg.x
        cmd.angular.z = error_x * self.kp_yaw
        
        # 2. PITCH PID: Keep target at a specific distance (bounding box area)
        current_area = msg.z
        error_area = self.target_area - current_area
        cmd.linear.x = error_area * self.kp_pitch
        
        # Clamp maximum speeds for safety
        cmd.angular.z = max(-1.0, min(1.0, cmd.angular.z))
        cmd.linear.x = max(-2.0, min(2.0, cmd.linear.x))
        
        # Publish command to ArduPilot GUIDED mode
        self.vel_pub.publish(cmd)
        self.get_logger().debug(f"Published Velocity - Vx: {cmd.linear.x:.2f}, Wz: {cmd.angular.z:.2f}")

def main(args=None):
    rclpy.init(args=args)
    pid_node = PIDControllerNode()
    rclpy.spin(pid_node)
    pid_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()