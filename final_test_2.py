from robomaster import robot
import time
import cv2
import numpy as np
import random
from unittest import result
import cv2 as cv
import numpy as np
import os
import torch
import cv2
from datetime import datetime
import keyboard
 
class MyRobot:
    def __init__(self):
        self.speed = 20
        self.x_val = 0.1
        self.y_val = 0.1
        self.delay = 0.25
        self.distance = 1000
        self.move_memory = []
        self.state_chicken = 0
        self.robot_status = ''
        self.name_1 = ''
        self.name_2 = ''
        self.name_3 = ''
        self.prob_1 = 0
        self.prob_2 = 0
        self.prob_3 = 0
        self.state_grip = 0
        self.state_side = 1
        self.state_row = 1
        self.ep_robot = robot.Robot()
        self.ep_robot.initialize(conn_type="ap")
        self.ep_ir = self.ep_robot.sensor
        self.ep_servo = self.ep_robot.servo
        self.ep_camera = self.ep_robot.camera
        self.ep_vision = self.ep_robot.vision
        self.ep_gripper = self.ep_robot.gripper
        self.ep_chassis = self.ep_robot.chassis
        self.ep_sensor_adaptor = self.ep_robot.sensor_adaptor
        self.model = torch.hub.load(r'C:\Users\user\Downloads\programming\robomaster\yolov5', 'custom', path=r'C:\Users\user\Downloads\programming\robomaster\best1.pt', source='local')
        # self.model = None
    def move_gripper(self, servo, degree):
        self.ep_servo.moveto(index=servo, angle= degree).wait_for_completed()
        time.sleep(1)
 
    def move_row(self, times):
        for i in range(25 * times):
            self.move_left()
 
    def check_row(self):
        if self.fl == 0 and self.fr == 0 and self.state_grip == 0:
            self.stop_moving()
            self.go_home(1.65)
            self.state_row += 1
        print(f'state_row : {self.state_row}')
 
   
    def open_gripper(self):
        self.ep_gripper.open(power=50)
        time.sleep(1)
 
    def close_gripper(self):
        self.ep_gripper.close()
        time.sleep(1)
 
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
 
        self.fl = self.ep_sensor_adaptor.get_io(id=1, port=1)
        self.fr = self.ep_sensor_adaptor.get_io(id=1, port=2)
        self.bl = self.ep_sensor_adaptor.get_io(id=2, port=1)
        self.br = self.ep_sensor_adaptor.get_io(id=2, port=2)
        time.sleep(0.01) # Delete Later Just Try
        # print(f'br: {br}, bl: {bl}, fl: {fl}, fr: {fr}, distance: {robott.distance}')
       
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
 
    def update_screen(self):
        self.img = self.ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
        # self.img = self.img[350:720, 180:1160]
 
    def display_camera(self):
        self.img = self.ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
        self.detect_stupid_chicken(self.img)
        cv2.waitKey(1)
 
    def close_camera(self):
        # Stop Camera
        self.ep_camera.stop_video_stream()
 
    def crop_videos(self, img):
        # Crop the videos
        img_cropped = img[100:620, 0:1280]
        return img_cropped

   
    def detect_stupid_chicken(self, screenshot):
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = (50, 50)
        fontScale = 1
        color = (255, 0, 0)
        thickness = 2
        self.result = self.model(screenshot, size=416)
 
        for i in range(len(self.result.pandas().xyxy)):
 
            try:
                df= self.result.pandas().xyxy[i]
            except:
                print('Status : Not Found ! ')
 
            try:
                self.name_1 = df.iloc[0, 6]
                xmin = int(df.iloc[0,0])
                ymin = int(df.iloc[0,1])
                xmax = int(df.iloc[0,2])
                ymax = int(df.iloc[0,3])
                self.prob_1 = df.iloc[0,4]
 
                print(f'name 1 : {self.name_1}\r')
                print(f'prob 1 : {self.prob_1} \r')
                if self.name_1 == 'dead':
                    self.move_to_chicken((xmin, ymin, abs(xmin - xmax), abs(ymin - ymax)), screenshot)
                    if self.prob_1 > 0.6:
                        self.state_chicken = 1
                    else:
                        self.state_chicken = 0
                    break
 
                # elif self.name_1 == 'alive':
                #     self.avoid_alive((xmin, ymin, abs(xmin - xmax), abs(ymin - ymax)), screenshot)
                #     if self.prob_1 > 0.6:
                #         self.state_chicken = 1
                #     else:
                #         self.state_chicken = 0
                #     break
 
                cv2.putText(screenshot, self.name_1, (xmin, ymin), font,
                    fontScale, color, thickness, cv2.LINE_AA)
                cv2.rectangle(screenshot, (xmin, ymin), (xmax, ymax), (255,0,0), 2)
 
               
                self.name_2 = df.iloc[1, 6]
                xmin = int(df.iloc[1,0])
                ymin = int(df.iloc[1,1])
                xmax = int(df.iloc[1,2])
                ymax = int(df.iloc[1,3])
                self.prob_2 = df.iloc[1,4]
 
                print(f'name 2 : {self.name_2}\r')
                print(f'prob 2 : {self.prob_2}\r')
                if self.name_2 == 'dead':
                    self.move_to_chicken((xmin, ymin, abs(xmin - xmax), abs(ymin - ymax)), screenshot)
                    if self.prob_2 > 0.6:
                        self.state_chicken = 1
                    else:
                        self.state_chicken = 0
                    break
 
                # elif self.name_2 == 'alive':
                #     self.avoid_alive((xmin, ymin, abs(xmin - xmax), abs(ymin - ymax)), screenshot)
                #     if self.prob_2 > 0.6:
                #         self.state_chicken = 1
                #     else:
                #         self.state_chicken = 0
                #     break
               
                cv2.putText(screenshot, self.name_2, (xmin, ymin), font,
                    fontScale, color, thickness, cv2.LINE_AA)
                cv2.rectangle(screenshot, (xmin, ymin), (xmax, ymax), (255,0,0), 2)
 
               
                self.name_3 = df.iloc[2, 6]
                xmin = int(df.iloc[2,0])
                ymin = int(df.iloc[2,1])
                xmax = int(df.iloc[2,2])
                ymax = int(df.iloc[2,3])
                self.prob_3 = df.iloc[2,4]
 
                print(f'name 3 : {self.name_3}\r')
                print(f'prob 3 : {self.prob_3}\r')
                if self.name_3 == 'dead':
                    self.move_to_chicken((xmin, ymin, abs(xmin - xmax), abs(ymin - ymax)), screenshot)
                    if self.prob_3 > 0.6:
                        self.state_chicken = 1
                    else:
                        self.state_chicken = 0
                    break
                   
                # elif self.name_3 == 'alive':
                #     self.avoid_alive((xmin, ymin, abs(xmin - xmax), abs(ymin - ymax)), screenshot)
                #     if self.prob_3 > 0.6:
                #         self.state_chicken = 1
                #     else:
                #         self.state_chicken = 0
                #     break
 
               
                cv2.putText(screenshot, self.name_3, (xmin, ymin), font,
                    fontScale, color, thickness, cv2.LINE_AA)
                cv2.rectangle(screenshot, (xmin, ymin), (xmax, ymax), (255,0,0), 2)
 
               
            except:
                pass    
 
        cv2.imshow("frame", screenshot)
           
    def move_left(self):
        self.stop_moving()
        self.ep_chassis.drive_wheels(w1=15, w2=-15, w3=15, w4=-15)
        time.sleep(self.delay)
        self.stop_moving()
        self.move_memory.append('left')
 
    def move_right(self):
        self.stop_moving()
        self.ep_chassis.drive_wheels(w1=-15, w2=15, w3=-15, w4=15)
        time.sleep(self.delay)
        self.stop_moving()
        self.move_memory.append('right')
   
    def gogetit(self, ir = 220):
        print('Status : Gogetit')
        # เดินไปข้างหน้าจนกว่าจะถึงระยะ ir แล้วค่อยหยิบ
        while self.distance >= ir:
            self.go_forward()
            self.stop_moving()
           
        self.open_gripper()
        self.update_screen()
        self.stop_moving()
        self.move_gripper(2, -80)
        # time.sleep(1)
        self.update_screen()
        self.move_gripper(1, 25)
        # time.sleep(1)
        self.go_forward()
        self.go_forward()
        self.stop_moving()
        self.update_screen()
        self.close_gripper()
        self.move_gripper(1, -0)
        self.move_gripper(2, -30)
        self.go_home(1.45)
        self.spin_back()
        self.update_screen()
        self.open_gripper()
        time.sleep(1)
        self.spin_back()
        self.update_screen()
        self.reset_gripper()
        self.state_chicken = 0
        self.name_1 = self.name_2 = self.name_3 = ''
        self.results = self.prob_1 = self.prob_2 = self.prob_3 = 0
       
        print('reset complete')
        time.sleep(1)
 
        print(self.state_chicken)
        print('Status : Finish Gogetit')
   
    def move_to_chicken (self, point, camera):
        chiken_center = point[0]+point[2]//2
        camera_center = camera.shape[1] //2
 
        if camera_center - 15 < chiken_center <  camera_center + 15:
            self.gogetit(200)
        elif camera_center < chiken_center :
            self.move_right()
        elif camera_center > chiken_center :
            self.move_left()
 
    def spin_back(self):
        self.ep_chassis.move(x=0, y=0, z= 180, z_speed=90).wait_for_completed()
        time.sleep(1)
 
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
   
    def go_forward(self):
        self.stop_moving()
        self.ep_chassis.drive_wheels(w1= self.speed, w2= self.speed , w3= self.speed , w4= self.speed)
        time.sleep(self.delay)
        self.stop_moving()
        self.move_memory.append('forward')
 
    def go_backward(self, speed = 1.45):
        self.stop_moving()
        self.ep_chassis.drive_wheels(w1= -self.speed * speed, w2= -self.speed * speed, w3= -self.speed * speed , w4= -self.speed * speed)
        time.sleep(self.delay)
        self.stop_moving()
        self.move_memory.append('back')
 
    def stop_moving(self):
        self.ep_chassis.drive_wheels(w1 = 0, w2 = 0 ,w3 = 0, w4 = 0)
 
    def go_home(self, speed):
        for i in self.move_memory[::-1]:
            if i == 'right':
                self.move_left()
 
            elif i == 'left':
                self.move_right()
 
            elif i == 'forward':
                self.go_backward(speed)
 
            elif i == 'back':
                self.go_forward()
 
        self.move_memory = []
        self.state_grip = 1
        self.state_side = 0
       
 
if __name__ == '__main__':
    robott = MyRobot()
    robott.reset_gripper() # Reset Gripper
    robott.start_ir() # Start IR Distance Sensor
    robott.read_sensor() # Read IR Sensor Value (0 or 1)
    robott.open_camera()
    robott.state_row = 2
    for i in range(35 * robott.state_row):
            robott.move_left()
    a = input()
    while True:
        try:
            robott.check_row()
            robott.state_grip = 0
            robott.read_sensor()
            print(str(robott.state_chicken) + '\r')
            robott.display_camera()
 
            if(cv2.waitKey(1) == ord('q')):
                cv2.destroyAllWindows()
                print('Stop Program')
                robott.stop_moving()
                robott.stop_ir()
                robott.close_camera()
               
                print('Shutdown Already')
                robott.ep_robot.close()
                exit()
           
            if robott.state_chicken == 0:
                print(f'state_row : {robott.state_row}, state_side : {robott.state_side}')
                if robott.state_row == 2 and robott.state_side == 0:
                    robott.move_row(1)
                    robott.state_side = 1
               
                elif robott.state_row == 3 and robott.state_side == 0:
                    robott.move_row(2)
                    robott.state_side = 1
 
                elif robott.state_row == 4 and robott.state_side == 0:
                    robott.move_row(3)
                    robott.state_side = 1
 
                robott.go_forward()
               
                pass
            else:
                robott.stop_moving()
            pass
 
        except KeyboardInterrupt:
            print('Stop Program')
            robott.stop_moving()
            robott.stop_ir()
            robott.close_camera()
            robott.ep_robot.close()
            print('Shutdown Already')