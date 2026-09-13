import rclpy 
from rclpy.node import Node 
from std_msgs.msg import Float32MultiArray
from std_msgs.msg import MultiArrayLayout, MultiArrayDimension


class HandPublisher(Node):
    def __init__(self):
        super().__init__('hand_publisher')
        self.publisher_ = self.create_publisher(Float32MultiArray, 'hand_data', 10)
        timer_period = 0.1 
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = Float32MultiArray()
        flat_data = []
        for i in range(21):
            x = float(i)
            y = float(i * 2)
            z = float(i * 3)
            
            flat_data.append(x)
            flat_data.append(y)
            flat_data.append(z)
        msg.data = flat_data
        self.publisher_.publish(msg)
        
        # Use the string formatting only for your visual log console!
        self.get_logger().info(f'Publishing Stamp: {self.i} | Data length: {len(msg.data)}')
        self.i += 1


def main(args=None):
    rclpy.init(args=args)
    hand_publisher = HandPublisher()
    rclpy.spin(hand_publisher)
    hand_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()