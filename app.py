from robomaster import robot
import time



class MyRobot:
    def __init__(self):
        self.ep_robot = robot.Robot()
        self.ep_robot.initialize(conn_type="ap")
        self.ep_ir = self.ep_robot.sensor
        self.ep_servo = self.ep_robot.servo
        self.ep_chassis = self.ep_robot.chassis
        self.ep_sensor_adaptor = self.ep_robot.sensor_adaptor
        self.ep_gripper = self.ep_robot.gripper
        self.delay = 0.25
        self.x_val = 0.1
        self.y_val = 0.1
        self.distance = 1000
        self.speed = 30

    def read_sensor(self):
        global fl 
        global fr
        global bl
        global br
        fl = self.ep_sensor_adaptor.get_io(id=1, port=1)
        fr = self.ep_sensor_adaptor.get_io(id=1, port=2)
        bl = self.ep_sensor_adaptor.get_io(id=2, port=1)
        br = self.ep_sensor_adaptor.get_io(id=2, port=2)
        print(f'br: {br}, bl: {bl}, fl: {fl}, fr: {fr}, distance: {robott.distance}')
        
    def sub_data_handler(self, sub_info):
        self.distance = sub_info[0]

    def start_ir(self):
        self.ep_ir.sub_distance(freq=5, callback=self.sub_data_handler)

    def stop_ir(self):
        self.ep_ir.unsub_distance()

    def reset_gripper(self):
        self.ep_servo.moveto(index=1, angle= 0).wait_for_completed()
        self.ep_servo.moveto(index=2, angle= 0).wait_for_completed()

    def go_forward(self):
        self.ep_chassis.drive_wheels(w1= 30, w2=30, w3=30, w4=30)
        time.sleep(self.delay)

    def turn_right_til_both_front_gone(self):
        while not (fl == 1 and fr == 1) or (br == 0 or bl == 0):
            self.ep_chassis.drive_wheels(w1=-self.speed, w2=self.speed, w3=-self.speed, w4=self.speed)
            time.sleep(self.delay)
            self.read_sensor()
            print('1')
        self.ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)

    def turn_left_til_back_right_gone(self):
        while not (br == 0 or (fl == 1 and fr == 1)):
            self.ep_chassis.drive_wheels(w1=self.speed, w2=-self.speed, w3=self.speed, w4=-self.speed)
            time.sleep(self.delay)
            self.read_sensor()
            print('2')
        self.ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)

    def turn_right_til_back_left_gone(self):
        while not (bl == 0 or (fl == 1 and fr == 1)):
            self.ep_chassis.drive_wheels(w1=-self.speed, w2=self.speed, w3=-self.speed, w4=self.speed)
            time.sleep(self.delay)
            self.read_sensor()
            print('3')
        self.ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)

    def turn_left_til_front_right_gone(self):
        while not ((fr == 1 and fl == 1) or (br == 0 or bl == 0)):
            self.ep_chassis.drive_wheels(w1=self.speed, w2=-self.speed, w3=self.speed, w4=-self.speed)
            time.sleep(self.delay)
            self.read_sensor()
            print('4')
        self.ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)

    def turn_right_til_front_left_gone(self):
        while not ((fr == 1 and fl == 1) or (br == 0 or bl == 0)):
            self.ep_chassis.drive_wheels(w1=-self.speed, w2=self.speed, w3=-self.speed, w4=self.speed)
            time.sleep(self.delay)
            self.read_sensor()
            print('5')
        self.ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)

    def pickup(self):

        self.stop_ir() # Stop IR Distance Sensor
        exit() # Exit Program

    def write_csv(self):
        # write csv file
        pass

    def find_flag(self):
        pass
    
if __name__ == '__main__':
    robott = MyRobot()
    robott.reset_gripper() # Reset Gripper 
    robott.start_ir() # Start IR Distance Sensor
    robott.read_sensor() # Read IR Sensor Value (0 or 1)

    while True:
        robott.read_sensor()
        if (br == 1 and bl == 1) and (fl == 0 and fr == 0): robott.turn_right_til_both_front_gone()
        if (br == 0) and (fl == 0 or fr == 0): robott.turn_left_til_back_right_gone()
        if (bl == 0) and (fl == 0 or fr == 0): robott.turn_right_til_back_left_gone()
        if (bl == 1 and br == 1) and (fl == 0 and fr == 1): robott.turn_right_til_front_left_gone()
        if (bl == 1 and br == 1) and (fl == 1 and fr == 0): robott.turn_left_til_front_right_gone()
        robott.go_forward()
        pass
        if robott.distance <= 6.2: robott.pickup()  
