from autoware_vehicle_msgs.msg import VelocityReport
import rclpy
from rclpy.node import Node


class Predkosc(Node):

    def __init__(self):
        super().__init__('predkosc')
        # (typ wiadomości, nazwa tematu, funkcja wołana po każdej wiadomości, długość kolejki)
        self.create_subscription(
            VelocityReport, '/vehicle/status/velocity_status', self.on_velocity, 10)

    def on_velocity(self, msg):
        kmh = msg.longitudinal_velocity * 3.6
        self.get_logger().info(f'prędkość: {kmh:.1f} km/h')


def main():
    rclpy.init()
    node = Predkosc()
    try:
        rclpy.spin(node)    # czeka na wiadomości i woła on_velocity, aż do Ctrl+C
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()