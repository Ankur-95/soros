import cv2
import rclpy 
from rclpy.node import Node 
from std_msgs.msg import Float32MultiArray
from std_msgs.msg import MultiArrayLayout, MultiArrayDimension

class Handpub(Node):
    def __init__(self):
        super().__init__('handpub')
        super.publisher_ = self.create_publisher(Float32MultiArray, 'hand_data', 10)
        timer_period = 0.03
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info('Hand Publisher Node has been started.')
#     def cam(self):
        # #theres no need of defining it separately right ?



    def timer_callback(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            exit()
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            # if frame is read correctly ret is True
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            # Display the resulting frame
            cv2.imshow('frame', frame)
        msg = Float32MultiArray()
        msg.layout = MultiArrayLayout(dim=[MultiArrayDimension(label='hand_data', size=21, stride=3)])
        msg.data = frame
        self.get_logger().info('Publishing hand data: "%s"' % msg.data)


def main(args=None):
    rclpy.init(args=args)
    handpub = Handpub()
    rclpy.spin(handpub)
    handpub.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()