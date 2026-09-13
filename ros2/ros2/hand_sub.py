import rclpy 
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray

class HandSubscriber(Node):
    def __init__(self):
        super().__init__('hand_subscriber')
        # Fixed: Changed self.subs to self.sub to match the function name below
        self.subscription = self.create_subscription(
            Float32MultiArray, 
            'hand_data', 
            self.sub, 
            10
        )

    def sub(self, msg):   
        # We want landmark index 5
        landmark_id = 5 
        
        # Calculate the starting slot: 5 * 3 = 15
        base_index = landmark_id * 3
        
        # Slice out the 3 coordinates from the flat list (indices 15, 16, 17)
        # msg.data is the actual Python list containing the 63 floats
        x = msg.data[base_index]
        y = msg.data[base_index + 1]
        z = msg.data[base_index + 2]
        
        # Log it visually to your console
        self.get_logger().info(f'Received Landmark 5 -> X: {x}, Y: {y}, Z: {z}')

def main(args=None):
    rclpy.init(args=args)
    hand_subscriber = HandSubscriber()
    rclpy.spin(hand_subscriber)
    hand_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
