import cv2
import os
import rclpy 
from rclpy.node import Node 
from std_msgs.msg import Float32MultiArray
import time 
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class Handpub(Node):
    def __init__(self):
        super().__init__('handpub')
        # Fix: Change super.publisher_ to self.publisher_
        self.publisher_ = self.create_publisher(Float32MultiArray, 'hand_data', 10)
        
        # 1. Initialize the camera ONCE when the node starts
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.get_logger().error("Cannot open camera hardware!")
            raise RuntimeError("Camera failed to open")
            
        timer_period = 0.033  # Roughly 30 Hz
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info('Hand Publisher Node has been started successfully.')
        
        # 2. Join it directly to your task file name
        model_path = '/home/ankur-95/soros/two_handlandmarker/two_handlandmarker/hand_landmarker.task'
        
        # 3. Log it so you can see exactly where it is looking on your system
        self.get_logger().info(f"Looking for model asset at: {model_path}")

        options = vision.HandLandmarkerOptions(
            # Pass the absolute path variable here!
            base_options=python.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_hands=1,
            result_callback=self.mp_callback  
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.frame_count = 0

    def timer_callback(self):
             # 2. Grab exactly ONE single frame per callback fire. No while loop!
            ret, frame = self.cap.read()
            if not ret:
                self.get_logger().warn("Can't receive frame (stream end?). Skipping this tick...")
                return  # Exit early so we don't crash
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            timestamp_ms = int(time.time_ns()//1_000_000)  # Convert nanoseconds to milliseconds
            self.detector.detect_async(mp_image, timestamp_ms)
            # Those were the primary steps and are no more needed.
                # # 3. For testing, show the frame visually
                # cv2.imshow('frame', frame)
                # cv2.waitKey(1) # Crucial: cv2.imshow requires waitKey(1) to actually render the window!
                
                # # Temporary placeholder logic just to see the loop running


                # # self.get_logger().info('Frame captured successfully!')
           


    def mp_callback(self, result: vision.HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        # This fires automatically whenever MediaPipe finishes running tracking on a frame
        self.frame_count += 1
        # 1. Force convert the MediaPipe frame into a standard, raw NumPy array
        canvas = np.array(output_image.numpy_view())

        # 2. Now OpenCV will accept it perfectly without crashing!
        canvas = cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR)
        flat_data = []
        if result.hand_landmarks:
            hand_landmarks = result.hand_landmarks[0]
            for landmark in hand_landmarks:
                flat_data.append(float(landmark.x))
                flat_data.append(float(landmark.y))
                flat_data.append(float(landmark.z))

                # Green Dots
                h,w, _ = canvas.shape
                cx, cy = int(landmark.x *w), int(landmark.y *h)
                cv2.circle(canvas, (cx, cy), 5,(0,255,0),cv2.FILLED)
        else:
            self.get_logger().info(f"No hand landmarks detected in frame {self.frame_count} at timestamp {timestamp_ms} ms.")
            flat_data = [0.0] * 63  # Fill with zeros if no landmarks are detected

        msg = Float32MultiArray()    
        self.publisher_.publish(msg)
        if self.frame_count % 30 == 0:  # Log every 30 frames
            hand_found = "TRACKING" if result.hand_landmarks else "NOT TRACKING"
            self.get_logger().info(f"Status: {hand_found}| Published array length: {len(msg.data)}")

        cv2.imshow('MediaPipe Tracking', canvas)
        cv2.waitKey(1)  # Ensure the window updates


        


def main(args=None):
    rclpy.init(args=args)
    handpub = Handpub()
    
    try:
        rclpy.spin(handpub)
    except KeyboardInterrupt:
        pass
    finally:
        if hasattr(handpub, 'detector'):
            handpub.detector.close()

        # 4. Clean exit strategy: Release the webcam when Ctrl+C is hit
        handpub.cap.release()
        cv2.destroyAllWindows()
        handpub.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()










































# import cv2
# import rclpy 
# from rclpy.node import Node 
# from std_msgs.msg import Float32MultiArray
# from std_msgs.msg import MultiArrayLayout, MultiArrayDimension

# class Handpub(Node):
#     def __init__(self):
#         super().__init__('handpub')
#         super.publisher_ = self.create_publisher(Float32MultiArray, 'hand_data', 10)
#         timer_period = 0.03
#         self.timer = self.create_timer(timer_period, self.timer_callback)
#         self.get_logger().info('Hand Publisher Node has been started.')
# #     def cam(self):
#         # #theres no need of defining it separately right ?



#     def timer_callback(self):
#         cap = cv2.VideoCapture(0)
#         if not cap.isOpened():
#             print("Cannot open camera")
#             exit()
#         while True:
#             # Capture frame-by-frame
#             ret, frame = cap.read()
#             # if frame is read correctly ret is True
#             if not ret:
#                 print("Can't receive frame (stream end?). Exiting ...")
#                 break
#             # Display the resulting frame
#             cv2.imshow('frame', frame)
#         msg = Float32MultiArray()
#         msg.layout = MultiArrayLayout(dim=[MultiArrayDimension(label='hand_data', size=21, stride=3)])
#         msg.data = frame
#         self.get_logger().info('Publishing hand data: "%s"' % msg.data)


# def main(args=None):
#     rclpy.init(args=args)
#     handpub = Handpub()
#     rclpy.spin(handpub)
#     handpub.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()