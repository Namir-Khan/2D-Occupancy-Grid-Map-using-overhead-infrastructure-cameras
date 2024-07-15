#!/usr/bin/env python3

# Importing the necessary libraries
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import glob
from PIL import Image as PILImage

class ImageListener(Node):

    def __init__(self):
        super().__init__('image_listener')
        self.bridge = CvBridge()
        self.imageStitcher = cv2.Stitcher_create()
        self.cv_image1 = None
        self.cv_image2 = None
        self.cv_image3 = None
        self.cv_image4 = None

        # Subscribe to the Camera1 Image topic
        self.subscription = self.create_subscription(
            Image,
            '/overhead_camera/overhead_camera1/image_raw',
            self.listener_callback,
            10)

        # Subscribe to the Camera2 Image topic
        self.subscription = self.create_subscription(
            Image,
            '/overhead_camera/overhead_camera2/image_raw',
            self.listener_callback2,
            10)
        
        # Subscribe to the Camera3 Image topic
        self.subscription = self.create_subscription(
            Image,
            '/overhead_camera/overhead_camera3/image_raw',
            self.listener_callback3,
            10)
        
        # Subscribe to the Camera4 Image topic
        self.subscription = self.create_subscription(
            Image,
            '/overhead_camera/overhead_camera4/image_raw',
            self.listener_callback4,
            10)

    def listener_callback(self, msg):
        self.get_logger().info('Receiving image 1')
        self.cv_image1 = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        self.check_and_stitch()
        # cv2.imshow("Camera Image", cv_image)
        # cv2.waitKey(1)

    def listener_callback2(self, msg):
        self.get_logger().info('Receiving image 2')
        self.cv_image2 = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        self.check_and_stitch()
        # cv2.imshow("Camera Image2", cv_image2)
        # cv2.waitKey(1)

    def listener_callback3(self, msg):
        self.get_logger().info('Receiving image 3')
        self.cv_image3 = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        self.check_and_stitch()
        # cv2.imshow("Camera Image3", cv_image3)
        # cv2.waitKey(1)

    def listener_callback4(self, msg):
        self.get_logger().info('Receiving image 4')
        self.cv_image4 = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        self.check_and_stitch()
        # cv2.imshow("Camera Image4", cv_image4)
        # cv2.waitKey(1)

    def check_and_stitch(self):
        if self.cv_image1 is not None and self.cv_image2 is not None and self.cv_image3 is not None and self.cv_image4 is not None:
            self.get_logger().info('All images received. Stitching...')
            cv2.imwrite("img1.png", self.cv_image1)
            cv2.imwrite("img2.png", self.cv_image2)
            cv2.imwrite("img3.png", self.cv_image3)
            cv2.imwrite("img4.png", self.cv_image4)
            map_output(self.imageStitcher, self.cv_image1, self.cv_image2, self.cv_image3, self.cv_image4)
            self.cv_image1 = None
            self.cv_image2 = None
            self.cv_image3 = None
            self.cv_image4 = None

# Img1 - Bottom Right
# Img2 - Bottom Left
# Img3 - Top Right
# Img4 - Top Left

def stitch_images(imageStitcher, img1, img2):
    error, stitched = imageStitcher.stitch([img1, img2])

    if error:
        print("Images could not be stitched!")
        exit()
    else:
        return stitched
    
def map_output(imageStitcher, img1, img2, img3, img4):
    top_stitched = stitch_images(imageStitcher, img4, img3)
    bottom_stitched = stitch_images(imageStitcher, img2, img1)
    
    top_stitched_rotate = cv2.rotate(top_stitched, cv2.ROTATE_90_COUNTERCLOCKWISE)
    bottom_stitched_rotate = cv2.rotate(bottom_stitched, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
    final_stitched = stitch_images(imageStitcher, bottom_stitched_rotate, top_stitched_rotate)
    
    final_stitched_rotate = cv2.rotate(final_stitched, cv2.ROTATE_90_CLOCKWISE)

    cv2.imwrite("GridMap.png", final_stitched_rotate)
    cv2.imshow("GridMap", final_stitched_rotate)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    map_img = PILImage.open('GridMap.png').convert('L')
    map_img.save('GridMap.pgm')


def main(args=None):
    rclpy.init(args=args)
    node = ImageListener()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
