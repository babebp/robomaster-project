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
        if white_pixel >= 19000:
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
        the_result = cv2.blur(mask, (10,10))
        return the_result

    def image_procession(self, image):
        cv2.imshow('original', image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower1 = np.array([0, 100, 20])
        upper1 = np.array([5, 255, 255])

        # upper boundary RED color range values; Hue (160 - 180)
        lower2 = np.array([160,100,20])
        upper2 = np.array([179,255,255])

        lower_mask = cv2.inRange(image, lower1, upper1)
        upper_mask = cv2.inRange(image, lower2, upper2)

        mask = lower_mask + upper_mask

        # cv2.rectangle(mask, (490,210), (790,510), (255, 255, 255)) 

        the_result = self.blur_pic(mask)
        
        n_white_pix = self.count_white_pixel(the_result)

        self.check_white(n_white_pix, the_result)
        
        cv2.imshow('result', the_result)

        return the_result

    def find_target(self, the_result):
        while True:
            # Get the image real-time
            img = self.ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
            the_result = self.detect_red(img)

            # Count white pixel in the middle of the picture
            sum_white = np.sum(the_result[210:510, 490:790] == 255) 
            print(f'sum : {sum_white}')

            # If white pixel more than 19000 will break while loop
            if sum_white >= 19000: 
                self.ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
                break
            else:
                self.ep_chassis.drive_wheels(w1=self.speed, w2=-self.speed, w3=-self.speed, w4=self.speed)
                time.sleep(self.delay)

        # Save image to see the result
        cv2.imwrite('result_raw', img)
        cv2.imwrite('result_finished', the_result)
        
        self.close_camera() # Close Camera
        self.stop_ir() # Stop IR Distance Sensor
        exit() # Exit Program

    def find_target_second_edition(self, the_result): 
        # Split Three parts left mid right
        # if left white pixel is the most then turn left until mid part is most
        # if right white pixel is them ost then turn right until mid part in most
        pass

    def pick_up(self):
        # Have to try how to grab that thing
        pass

    def turn_left(self):
        self.ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
        while True : # ทำไปเรื่อยๆ ขณะที่หน้าเป็น 0 
            if bl == 0 or (fl == fr == 1):
                self.ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
                break

            self.ep_chassis.drive_wheels(w1=self.speed, w2=-self.speed, w3=self.speed, w4=-self.speed)
            time.sleep(self.delay)
            self.read_sensor()
            time.sleep(self.delay)
            print('Turning Left')

    def turn_right(self):
        self.ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
        while True:
            if br == 0 or (fl == fr == 1):
                self.ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
                break

            self.ep_chassis.drive_wheels(w1=-self.speed, w2=self.speed, w3=-self.speed, w4=self.speed)
            time.sleep(self.delay)
            self.read_sensor()
            time.sleep(self.delay)
            print('Turning Right')
    
    def go_forward(self):
        self.ep_chassis.drive_wheels(w1= self.speed, w2= self.speed , w3= self.speed , w4= self.speed)
        time.sleep(self.delay)

if __name__ == '__main__':
    robott = MyRobot()
    robott.reset_gripper() # Reset Gripper 
    robott.start_ir() # Start IR Distance Sensor
    robott.read_sensor() # Read IR Sensor Value (0 or 1)
    robott.open_camera()

    while True:
        robott.read_sensor()
        robott.display_camera()
        
        if br == 0 or fr == 0: robott.turn_left()
        if bl == 0 or fl == 0: robott.turn_right()
        else: robott.go_forward()
        pass
