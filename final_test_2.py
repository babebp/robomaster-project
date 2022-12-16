from re import L
from turtle import distance
from robomaster import robot
import time
import cv2
import numpy as np

class MyRobot:
    def __init__(self):
        self.speed = 15
        self.x_val = 0.1
        self.y_val = 0.1
        self.delay = 0.25
        self.distance = 1000

        self.ep_robot = robot.Robot()
        self.ep_robot.initialize(conn_type="ap")
        self.ep_ir = self.ep_robot.sensor
        self.ep_servo = self.ep_robot.servo
        self.ep_camera = self.ep_robot.camera
        self.ep_vision = self.ep_robot.vision
        self.ep_gripper = self.ep_robot.gripper
        self.ep_chassis = self.ep_robot.chassis
        self.ep_sensor_adaptor = self.ep_robot.sensor_adaptor
    
    def move_gripper(self, servo, degree):
        self.ep_servo.moveto(index=servo, angle= degree).wait_for_completed()
        time.sleep(2)

    def open_gripper(self):
        self.ep_gripper.open(power=50)
        time.sleep(2)

    def close_gripper(self):
        self.ep_gripper.close()
        time.sleep(2)

    def read_sensor(self):
        # Read 4 Ir sensors ( 1 or 0 )
        global fl # Front Left
        global fr # Front Right
        global bl # Back Left
        global br # Back Right
        fl = self.ep_sensor_adaptor.get_io(id=1, port=1)
        fr = self.ep_sensor_adaptor.get_io(id=1, port=2)
        bl = self.ep_sensor_adaptor.get_io(id=2, port=1)
        br = self.ep_sensor_adaptor.get_io(id=2, port=2)
        time.sleep(0.01) # Delete Later Just Try
        print(f'br: {br}, bl: {bl}, fl: {fl}, fr: {fr}, distance: {robott.distance}')
        
    def sub_data_handler(self, sub_info):
        # Use for read IR distance
        self.distance = sub_info[0]

    def start_ir(self):
        # Start IR distance
        self.ep_ir.sub_distance(freq=5, callback=self.sub_data_handler)

    def stop_ir(self):
        # Stop IR distance
        self.ep_ir.unsub_distance()

    def reset_gripper(self):
        # Move gripper to 0 degree
        self.ep_servo.moveto(index=1, angle= 0).wait_for_completed()
        self.ep_servo.moveto(index=2, angle= 0).wait_for_completed()
        self.ep_gripper.open(power = 50)

    def open_camera(self):
        # Start Camera
        self.ep_camera.start_video_stream(display=False)
        time.sleep(self.delay)

    def display_camera(self):
        # Show the image real-time
        img = self.ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
        self.image_procession(img)
        cv2.waitKey(1)

    def close_camera(self):
        # Stop Camera
        self.ep_camera.stop_video_stream()

    def crop_videos(self, img):
        # Crop the videos
        img_cropped = img[100:620, 0:1280]
        return img_cropped

    def count_white_pixel(self, the_result):
        # Count white pixel in the image (the_result)
        n_white_pix = np.sum(the_result == 255)
        print(n_white_pix)
        return n_white_pix

    def check_white(self, white_pixel, the_result):
        # Check if white pixel more than 19000 will go to find_target
        if white_pixel >= 17000:
            self.find_target(the_result)

    def detect_red(self, image):
        # Detect Red and Blur
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower1 = np.array([0, 100, 20])
        upper1 = np.array([5, 255, 255])

        # upper boundary RED color range values; Hue (160 - 180)
        lower2 = np.array([160,100,20])
        upper2 = np.array([179,255,255])

        lower_mask = cv2.inRange(image, lower1, upper1)
        upper_mask = cv2.inRange(image, lower2, upper2)

        mask = lower_mask + upper_mask

        the_result = self.blur_pic(mask)

        return the_result

    def blur_pic(self, mask):
        the_result = cv2.blur(mask, (5,5))
        return the_result

    def image_procession(self, image):
        cv2.imshow('original', image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # lower1 = np.array([0, 100, 20])
        # upper1 = np.array([5, 255, 255])

        # # upper boundary RED color range values; Hue (160 - 180)
        # lower2 = np.array([160,100,20])
        # upper2 = np.array([179,255,255])

        # lower1 = np.array([0, 100, 200])
        # upper1 = np.array([20, 255, 255])

        lower1 = np.array([30, 100, 100])
        upper1 = np.array([40, 255, 255])

        lower2 = np.array([0,100,200])
        upper2 = np.array([20,255,255])
        
        lower_mask = cv2.inRange(image, lower1, upper1)
        upper_mask = cv2.inRange(image, lower2, upper2)

        mask = lower_mask + upper_mask

        # cv2.rectangle(mask, (490,210), (790,510), (255, 255, 255)) 
        # the_result = mask
        the_result = self.blur_pic(mask)
        
        the_result = self.draw_rectangular(the_result)
        # n_white_pix = self.count_white_pixel(the_result)

        # self.check_white(n_white_pix, the_result)
        cv2.imwrite('result.png', the_result)
        cv2.imshow('result', the_result)
        
        return the_result

    def find_target(self, the_result):
        self.stop_moving()
        while True:
            # Get the image real-time
            img = self.ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
            the_result = self.detect_red(img)

            # Count white pixel in the middle of the picture
            sum_white = np.sum(the_result[210:510, 490:790] == 255) 
            print(f'sum : {sum_white}')

            # If white pixel more than 19000 will break while loop
            if sum_white >= 7000: 
                print('Finish Spin')
                self.stop_moving()
                print('Find Target')
                self.move_to_target()
                print('Pickup')
                self.pickup()
                self.close_camera() # Close Camera
                self.stop_ir() # Stop IR Distance Sensor
                exit() # Exit Program
                break
                
            else:
                self.ep_chassis.drive_wheels(w1=self.speed, w2=-self.speed, w3=-self.speed, w4=self.speed)
                time.sleep(self.delay)

        
        # self.close_camera() # Close Camera
        # self.stop_ir() # Stop IR Distance Sensor
        # exit() # Exit Program

    def find_target_second_edition(self, the_result): 
        self.stop_moving()
        # Split Three parts left mid right
        left_side = np.sum(the_result[0:720, 0:425] == 255)
        middle = np.sum(the_result[0:720, 425:850] == 255)
        right_side = np.sum(the_result[0:720, 850:1280] == 255)

        # if left white pixel is the most then turn left until mid part is most
        if left_side < middle and left_side < right_side: self.spin('left')
        # if right white pixel is them ost then turn right until mid part in most
        if right_side < middle and right_side < left_side: self.spin('right')
        # if middle is the most white pixel
        else: self.move_to_target()

    # def spin(self, direction):
    #     if direction.lower() == 'right': 
    #         while True:
    #             img = self.ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
    #             the_result = self.detect_red(img)

    #             left_side = np.sum(the_result[0:720, 0:425] == 255)
    #             middle = np.sum(the_result[0:720, 425:850] == 255)
    #             right_side = np.sum(the_result[0:720, 850:1280] == 255)

    #             if middle < left_side and middle < right_side:
    #                 self.stop_moving()
    #                 break

    #             self.ep_chassis.drive_wheels(w1=self.speed, w2=-self.speed, w3=-self.speed, w4=self.speed)
    #             time.sleep(self.delay)

    #     if direction.lower() == 'left':
    #         while True:
    #             img = self.ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
    #             the_result = self.detect_red(img)

    #             left_side = np.sum(the_result[0:720, 0:425] == 255)
    #             middle = np.sum(the_result[0:720, 425:850] == 255)
    #             right_side = np.sum(the_result[0:720, 850:1280] == 255)

    #             if middle < left_side and middle < right_side:
    #                 self.stop_moving()
    #                 break

    #             self.ep_chassis.drive_wheels(w1=-self.speed, w2=self.speed, w3=self.speed, w4=-self.speed)
    #             time.sleep(self.delay)

    def pickup(self):
        self.move_gripper(2, -90)
        self.close_gripper()
        pass

    def move_to_target(self):
        # Have to try how to grab that thing
        while True:
            if robott.distance <= 147:
                self.stop_moving()
                break
            else:
                self.go_forward()
        pass

    def turn_left(self):
        self.stop_moving()
        while True : # ทำไปเรื่อยๆ ขณะที่หน้าเป็น 0 
            if bl == 0 or (fl == fr == 1):
                self.stop_moving()
                break

            self.ep_chassis.drive_wheels(w1=self.speed, w2=-self.speed, w3=self.speed, w4=-self.speed)
            time.sleep(self.delay)
            self.read_sensor()
            time.sleep(self.delay)
            print('Turning Left')

    def turn_right(self):
        self.stop_moving()
        while True:
            if br == 0 or (fl == fr == 1):
                self.stop_moving()
                break

            self.ep_chassis.drive_wheels(w1=-self.speed, w2=self.speed, w3=-self.speed, w4=self.speed)
            time.sleep(self.delay)
            self.read_sensor()
            time.sleep(self.delay)
            print('Turning Right')
    
    def go_forward(self):
        self.ep_chassis.drive_wheels(w1= self.speed, w2= self.speed , w3= self.speed , w4= self.speed)
        time.sleep(self.delay)

    def stop_moving(self):
        self.ep_chassis.drive_wheels(w1 = 0, w2 = 0 ,w3 = 0, w4 = 0)

    def draw_rectangular(self, mask):
        image = mask
        paper = image[180:image.shape[0], 0:image.shape[1]]
        _ , thresh_gray = cv2.threshold(image, 254, 255, cv2.THRESH_BINARY)
        thresh_gray = thresh_gray[180:image.shape[0], 0:image.shape[1]]

        thresh_gray = cv2.morphologyEx(thresh_gray, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (51,51)))

        # Find contours in thresh_gray after closing the gaps
        contours, _ = cv2.findContours(thresh_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        for c in contours:
            area = cv2.contourArea(c)
            (x, y, w, h) = cv2.boundingRect(c)
            # Small contours are ignored.
            if (area < 500) or (w < h) :
                cv2.fillPoly(thresh_gray, pts=[c], color=0)
                continue

            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            # convert all coordinates floating point values to int
            box = np.int0(box)
            cv2.drawContours(paper, [box], 0, (255, 255, 255), 2)

        return paper
        
if __name__ == '__main__':
    robott = MyRobot()
    robott.reset_gripper() # Reset Gripper 
    robott.start_ir() # Start IR Distance Sensor
    robott.read_sensor() # Read IR Sensor Value (0 or 1)
    robott.open_camera()

    while True:
        try:
            robott.read_sensor()
            robott.display_camera()

            #if br == 0 or fr == 0: robott.turn_left()
            #if bl == 0 or fl == 0: robott.turn_right()
            #else: robott.go_forward()
            #pass

        except KeyboardInterrupt:
            print('Stop Program')
            robott.stop_moving()
            robott.stop_ir()
            robott.close_camera()
            print('Shutdown Already')


# if spin not work try delay and move a little
# find pickup algorithms