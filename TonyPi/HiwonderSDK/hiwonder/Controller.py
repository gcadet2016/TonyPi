# Controller.py
# V1.1 date: 2024-12-23
#
# Path: TonyPi\HiwonderSDK\hiwonder\Controller.py
from . import ros_robot_controller_sdk as rrc
import time

board = rrc.Board()


class Controller:
    def __init__(self, board, time_out=50):
        self.board = board
        self.time_out = time_out

    """
        function name： obtain bus servo temperature limit
        param：
                servo_id: to obtain the servo id of temperature limit
        return：   return the servo temperature limit
    """ 
    def get_bus_servo_temp_limit(self, servo_id):
        count = 0
        while True:
            data = self.board.bus_servo_read_temp_limit(servo_id)
            count += 1
            if data is not None:
                return data[0]
            if count > self.time_out:
                return None
            time.sleep(0.01)

    """
        Get the bus servo angle limit for the servo_id
        param：servo_id int
        return： return a 2 values tuple for the servo angle limits
    """ 
    def get_bus_servo_angle_limit(self, servo_id):
        count = 0
        while True:
            data = self.board.bus_servo_read_angle_limit(servo_id)
            count += 1
            if data is not None:
                return data                 # Bug fixed
            if count > self.time_out:
                return None
            time.sleep(0.01)
    

    """
        Get bus servo voltage limit for the servoId
        param：servo_id int
        return： return a 2 values tuple for the servo voltage limits
    """ 
    def get_bus_servo_vin_limit(self, servo_id):
        count = 0
        while True:
            data = self.board.bus_servo_read_vin_limit(servo_id)
            count += 1
            if data is not None:
                return data                 # bug fixed
            if count > self.time_out:
                return None
            time.sleep(0.01)
    

    """
        Get bus servo ID and return the first one (Note: only one servo should be connected)
        param：na
        return：return servo ID (int)
    """      
    def get_bus_servo_id(self):
        count = 0
        while True:
            data = self.board.bus_servo_read_id()
            count += 1
            if data is not None:
                return data[0]
            if count > self.time_out:
                return None
            time.sleep(0.01)
    

    """
        function name： get bus servo current position
        param：servo_id int
        return： return servo current position [0, 1000]
    """      
    def get_bus_servo_pulse(self, servo_id):
        count = 0
        while True:
            data = self.board.bus_servo_read_position(servo_id)
            count += 1
            if data is not None:
                return data[0]
            if count > self.time_out:
                return None
            time.sleep(0.01)
   

    """
        function name：get bus servo voltage
        param：servo_id
        return：return servo current voltage
    """  
    def get_bus_servo_vin(self, servo_id):
        count = 0
        while True:
            data = self.board.bus_servo_read_vin(servo_id)
            count += 1
            if data is not None:
                return data[0]
            if count > self.time_out:
                return None
            time.sleep(0.01)
    

    """
        function name：get bus servo current temperature
        param：servo_id int
        return：return servo current temperature
    """  
    def get_bus_servo_temp(self, servo_id):
        count = 0
        while True:
            data = self.board.bus_servo_read_temp(servo_id)
            count += 1
            if data is not None:
                return data[0]
            if count > self.time_out:
                return None
            time.sleep(0.01)
    

    """
        function name：obtain bus servo deviation
        param：servo_id int
        return：return servo deviation
    """    
    def get_bus_servo_deviation(self, servo_id):
        count = 0
        while True:
            data = self.board.bus_servo_read_offset(servo_id)
            count += 1
            if data is not None:
                return data[0]
            if count > self.time_out:
                return None
            time.sleep(0.01)
    

    """
        function name： set bus servo position
        param：
                servo_id: the id of the servo to be driven
                pulse:    servo target position
                use_time: the time required for rotation (ms)
    """
    def set_bus_servo_pulse(self, servo_id, pulse, use_time):
        self.board.bus_servo_set_position(use_time/1000, [[servo_id, pulse]])

    """
        function name：set pwm servo position
        param：
                servo_id: the servo id needed to be driven
                pulse: servo target position
                use_time: the time needed to rotate
    """
    def set_pwm_servo_pulse(self, servo_id, pulse, use_time):
        self.board.pwm_servo_set_position(use_time/1000, [[servo_id, pulse]])

    """
        function name：set bus servo ID
        param：
                servo_id_now: current servo ID
                servo_id_new: new servo ID
    """
    def set_bus_servo_id(self, servo_id_now, servo_id_new):
        self.board.bus_servo_set_id(servo_id_now, servo_id_new)

    """
        function name：set bus servo deviation
        param：
                servo_id: the servo ID needed to be set
                deviation: set the servo deviation
    """
    def set_bus_servo_deviation(self, servo_id, deviation):
        self.board.bus_servo_set_offset(servo_id, deviation)

    """
        function name：set bus servo temperature limit
        param：
                servo_id: servo ID needed to be set
                temp_limit: set the temperature limit
    """
    def set_bus_servo_temp_limit(self, servo_id, temp_limit):
        self.board.bus_servo_set_temp_limit(servo_id, temp_limit)

    """
        function name：set bus servo angle limit
        param：
                servo_id: servo ID needed to be set
                angle_limit: set the angle limit (tuple: angle_min, angle_max)
    """
    def set_bus_servo_angle_limit(self, servo_id, angle_limit):
        self.board.bus_servo_set_angle_limit(servo_id, angle_limit)

    """
        function name：set bus servo voltage limit
        param：
                servo_id: servo ID to be set
                vin_limit: set the voltage limit (tuple: vin_min, vin_max)
    """
    def set_bus_servo_vin_limit(self, servo_id, vin_limit):
        self.board.bus_servo_set_vin_limit(servo_id, vin_limit)

    """
        function name：download servo deviation
        param：servo_id: the ID of the servo to configure the deviation
    """    
    def save_bus_servo_deviation(self, servo_id):
        self.board.bus_servo_save_offset(servo_id)

    """
        function name：servo loss the power
        param： servo_id: the ID of the servo to loss power
    """ 
    def unload_bus_servo(self, servo_id):
        self.board.bus_servo_enable_torque(servo_id, 1)

    """
        function name：drive the buzzer
        param：
                freq:     sound frequency
                on_time： turn on time
                off_time: turn off time
                repeat：  repetition times
    """ 
    def set_buzzer(self, freq, on_time, off_time, repeat=1):
        self.board.set_buzzer(freq, on_time, off_time, repeat=1)

    """
        function name： get imu data
        param：
        return：IMU data, ax, ay, az, gx, gy, gz
    """ 
    def get_imu(self):
        count = 0
        while True:
            data = self.board.get_imu()
            count += 1
            if data is not None:
                return data
            if count > self.time_out:
                return None
            time.sleep(0.01)

    """
        function name： data reception enable
        param：
        return：
    """ 
    def enable_recv(self):
        self.board.enable_reception(False)
        time.sleep(1)
        self.board.enable_reception(True)
        time.sleep(1)
        
    