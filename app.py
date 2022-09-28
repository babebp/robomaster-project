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
        self.delay = time.sleep(0.25)

        self.distance = 1000

    def read_sensor(self):
        global fl 
        global fr
        global bl
        global br
        fl = self.ep_sensor_adaptor.get_io(id=1, port=1)
        fr = self.ep_sensor_adaptor.get_io(id=1, port=2)
        bl = self.ep_sensor_adaptor.get_io(id=2, port=1)
        br = self.ep_sensor_adaptor.get_io(id=2, port=2)
        
    def sub_data_handler(self, sub_info):
        self.distance = sub_info[0]


    def start_ir(self):
        self.ep_ir.sub_distance(freq=5, callback=self.sub_data_handler)

    def stop_ir(self):
        self.ep_ir.unsub_distance()

    def reset_gripper(self):
        self.ep_servo.moveto(index=1, angle= 0).wait_for_completed()
        self.ep_servo.moveto(index=2, angle= 0).wait_for_completed()

    def turn_left(self, until):
        while not until:
            # Turn Left
            pass

    def turn_right(self, until):
        while not until:
            # Turn Right
            pass

    def pickup(self):
        # Pick the Flag
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
        # if (br == 1 and bl == 1) and (fl == 0 and fr == 0): robott.turn_right(( (fl == 1 and fr == 1) or (br == 0 or bl == 0) ))
        # if (br == 0) and (fl == 0 or fr == 0): robott.turn_left((br == 1 and (fl == 1 and fr == 1)))
        # if (bl == 0) and (fl == 0 or fr == 0): robott.turn_right((bl == 1 and (fl == 1 and fr == 1)))
        # if (bl == 1 and br == 1) and (fl == 0 and fr == 1): robott.turn_right(fl == 1)
        # if (bl == 1 and br == 1) and (fl == 1 and fr == 0): robott.turn_left(fr == 1)
        # if robott.distance <= 6.2: robott.pickup()  

        print(f'br: {br}, bl: {bl}, fl: {fl}, fr: {fr}, distance: {robott.distance}')