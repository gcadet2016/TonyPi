# config_bus_servo.py
# Version 1.2
#
# Configure serial bus servo
#
# This code comes from BUS_Servo_Tool source code
# Caution: read the documentation for servo connection
#   
import os
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller
import cv2
import time

DEBUG = True
MAXSERVOID = 18               # 16 + hands = 18


# Enable or disable actions
# Exemples (options not mentionned are set to False)
#
# 1- Read all servos settings
# DISCOVER_ALL_SERVOS = True
#
# 2- Reconfigure all servos
# RECONFIGURE_ALL_SERVOS = True
# DISCOVER_ALL_SERVOS = True 

DISCOVER_NEW_AND_SINGLE_SERVO = False           # required: only one servo connected to the bus
READ_SERVO_DATA_BEFORE_CHANGING_ID = False      # required parameter: currentServoId in __main__
UPDATE_SERVO_ID = False                         # required parameter: currentServoId & newServoId in __main__
UPDATE_SERVO_CONFIG = False                     # required parameter: currentServoId & newServoId in __main__
READ_SERVO_DATA_AFTER_CHANGE = False            # required parameter: currentServoId & newServoId in __main__
RECONFIGURE_ALL_SERVOS = False
DISCOVER_ALL_SERVOS = True 
MOVE_SERVO = False                              # required parameter: newServoId in __main__


def print_err(s):
    print(f'ERROR: {s}')

def debug_print(s):
    if DEBUG:
        print(s)
# In the following table, pos value comes from stand_slow.d6a (run by TonyPi.py on start-up)
#               servoId: [deviation, temp, pos, pos_min, pos_max, vin-min, vin_max]
servos_settings = { 1: [0, 60, 500, 0, 1000, 4500, 14000],
                   2: [0, 60, 388, 0, 1000, 4500, 14000],
                   3: [0, 60, 500, 0, 1000, 4500, 14000],
                   4: [-25, 60, 594, 0, 1000, 4500, 14000],
                   5: [-7, 65, 500, 3, 990, 4600, 13000],
                   6: [-14, 60, 575, 0, 1000, 4500, 14000],
                   7: [0, 60, 800, 0, 1000, 4500, 14000],
                   8: [-28, 60, 725, 0, 1000, 4500, 14000],
                   9: [0, 60, 500, 0, 1000, 4500, 14000],
                   10: [0, 60, 612, 0, 1000, 4500, 14000],
                   11: [0, 60, 500, 0, 1000, 4500, 14000],
                   12: [12, 60, 406, 0, 1000, 4500, 14000],
                   13: [-6, 60, 500, 0, 1000, 4500, 14000],
                   14: [0, 60, 425, 0, 1000, 4500, 14000],
                   15: [0, 60, 200, 0, 1000, 4500, 14000],
                   16: [0, 60, 275, 0, 1000, 4500, 14000],
                   17: [0, 60, 500, 0, 1000, 4500, 14000],
                   18: [0, 60, 500, 0, 1000, 4500, 14000]
                 }


# Source code: /home/pi/Bus_Servo_Tool/main.py
class ServoBus():
    def __init__(self):
        self.IdProvided = False
        self.id = 0
        self.readOrNot = False
        self.deviation = 0
        self.servoTempLimit = 0
        self.servoMin = 0           # max and min position
        self.servoMax = 0
        self.servoMinV = 0          # max and min voltage
        self.servoMaxV = 0
        self.servoPulse = 0
        self.discovered_servos_settings = {}

        print('Stopping tonypi service')
        os.system("sudo systemctl stop tonypi")

        print('Board controller instanciation')
        self.board = rrc.Board()
        self.board.enable_reception()
        self.ctl = Controller(self.board)

    # If servoId = -1 : discover single servo connected
    # If servoId> 1 and <=18  read is validated and set operation
    def run(self, name, servoId=-1, deviation=0, temp=85, pos=500, pos_min=0, pos_max=1000, vin_min=4.5, vin_max=14):

        # ------find--------------------------
        # Requied: only one servo connected
        if name == 'find':
            print('Starting servoBus.find command')
            try:
                print('Calling get_bus_servo_id()')
                self.id = self.ctl.get_bus_servo_id()       # get the first servi id
                if self.id is None:
                    print_err('Servo not found')
                    return
                self.readOrNot = True

                # else:
                #     print('Calling Board.bus_servo_read_id()')

                print('calling get_bus_servo_deviation')
                self.deviation = self.ctl.get_bus_servo_deviation(self.id)
                if self.deviation > 125:
                    self.deviation = -(0xff-(self.deviation - 1))

                print('calling get_bus_servo_temp_limit')
                self.servoTempLimit = self.ctl.get_bus_servo_temp_limit(self.id)

                print('calling get_bus_servo_angle_limit')
                (self.servoMin, self.servoMax) = self.ctl.get_bus_servo_angle_limit(self.id)

                print('calling get_bus_servo_vin_limit')
                (self.servoMinV, self.servoMaxV) = self.ctl.get_bus_servo_vin_limit(self.id)

                print('calling get_bus_servo_pulse')
                self.servoPulse = self.ctl.get_bus_servo_pulse(self.id)
                
                print('calling get_bus_servo_vin')
                currentVin = self.ctl.get_bus_servo_vin(self.id)

                print('calling get_bus_servo_temp')
                currentTemp = self.ctl.get_bus_servo_temp(self.id)

                print(f'Servo Id    {self.id}')
                print(f'deviation   {self.deviation}')
                
                print(f'TempLimit   {self.servoTempLimit}°C')
                print(f'Min pulse   {self.servoMin}')
                print(f'Max pulse   {self.servoMax}')
           
                print(f'Min V       {self.servoMinV}mV')
                print(f'Max V       {self.servoMaxV}mV')

                print(f'current pulse {self.servoPulse}')
                print(f'current Vin   {currentVin}mV')
                print(f'current Temp  {currentTemp}°C')

            except:
                print_err('run exception: Find command raised an exception')
                return
                    
        # ------read--------------------------
        # If a servoId value is provided : try to read the servo
        # If servoId = -1 (no value provided) : find a servo
        # output: if servo read is successsful -> self.id is updated and self.readOrNot = True
        if name == 'read':
            print('Starting servoBus.read command')
            try:
                if servoId <= 0:
                    print('Search for a servo - Calling get_bus_servo_id()')
                    self.id = self.ctl.get_bus_servo_id()       # get the first servo id
                    if self.id is None:
                        print_err('No servo found')
                        return
                    self.readOrNot = True
                else:
                    if (1 <= servoId <= MAXSERVOID):
                        print(f'Trying to read servo {servoId} settings')
                        self.id = servoId
                    else:
                        print_err(f'Invalid servoId value: {servoId}')
                        return
                # else:
                #     print('Calling Board.bus_servo_read_id()')

                print('calling get_bus_servo_deviation')
                self.deviation = self.ctl.get_bus_servo_deviation(servoId)
                if self.deviation is None:
                    print_err(f'Servo {servoId} not found')
                    self.readOrNot = False
                    self.id = 0
                    return
                else:
                    self.readOrNot = True

                    if self.deviation > 125:
                        self.deviation = -(0xff-(self.deviation - 1))

                print('calling get_bus_servo_temp_limit')
                self.servoTempLimit = self.ctl.get_bus_servo_temp_limit(self.id)

                print('calling get_bus_servo_angle_limit')
                (self.servoMin, self.servoMax) = self.ctl.get_bus_servo_angle_limit(self.id)

                print('calling get_bus_servo_vin_limit')
                (self.servoMinV, self.servoMaxV) = self.ctl.get_bus_servo_vin_limit(self.id)

                print('calling get_bus_servo_pulse')
                self.servoPulse = self.ctl.get_bus_servo_pulse(self.id)
                
                print('calling get_bus_servo_vin')
                currentVin = self.ctl.get_bus_servo_vin(self.id)

                print('calling get_bus_servo_temp')
                currentTemp = self.ctl.get_bus_servo_temp(self.id)

                print(f'Servo Id    {self.id}')
                print(f'deviation   {self.deviation}')
                
                print(f'TempLimit   {self.servoTempLimit}°C')
                print(f'Min pulse   {self.servoMin}')
                print(f'Max pulse   {self.servoMax}')
           
                print(f'Min V       {self.servoMinV}mV')
                print(f'Max V       {self.servoMaxV}mV')

                print(f'current pulse {self.servoPulse}')
                print(f'current Vin   {currentVin}mV')
                print(f'current Temp  {currentTemp}°C')

            except:
                print_err('run exception: Read timeout?')
                self.id = 0
                self.readOrNot = False
                return

      # ------update servoId only----------
        # Parameter servoId contain the new servo Id
        elif name == 'setId':
            print('Starting servoBus setId command')
            if self.readOrNot is False:
                print_err('call read of find first！')  # during the read step we update self.Id with the current servo id
                return
            
            self.readOrNot = False
            if not(1 <= servoId <= MAXSERVOID):         # new servo Id
                print_err(f'Invalid servoId parameter: {servoId}')
                return
            
            print(f'Configure servo id: actual id= {self.id}, new id= {servoId}')
            self.ctl.set_bus_servo_id(self.id, servoId) # update servo Id
            #time.sleep(0.01)
            # if not self.IdProvided:                 # only one servo connected ==> Let rediscover dans validate the Id
            #     d = self.ctl.get_bus_servo_id()
            #     if d != servoId:
            #         print_err(f'Fail to update servoId. ID readen from servo: {d}')
            #         return
            #     else:
            #         print('success')            

        # ------set--------------------------
        elif name == 'set':
            print('Starting servoBus set command')
            if (self.readOrNot is False) or (self.id != servoId):
                print_err('call read first！')
                return
            
            # self.readOrNot = False
            if not(1 <= servoId <= MAXSERVOID):
                print_err(f'Invalid servoId parameter: {servoId}')
                return           

            if not(-125 < deviation < 125):
                print_err('Deviation out of range [-125,125]')
                print_err(f'Deviation: {deviation}')
                return          

            if not((0 <= pos_min <= 1000) and (0 <= pos_max <= 1000) and (pos_min < pos_max)):
                print_err('Invalid pos_min/pos_max values ([0,1000] and pos_min < pos_max)')
                print_err(f'pos_min: {pos_min}, pos_max: {pos_max}')
                return

            if not((4500 <= vin_min <= 14000) and (4500 <= vin_max <= 14000) and (vin_min < vin_max)):
                print_err('Invalid vin_min/vin_max values ([4500,14000] and vin_min < vin_max)')
                print_err(f'vin_min: {vin_min}, vin_max: {vin_max}')
                return
            
            print('Parameters validated')
              
            print(f'set_bus_servo_deviation(id={servoId}, deviation={deviation})')
            self.ctl.set_bus_servo_deviation(servoId, deviation) # update servo deviation
            time.sleep(0.01)
            self.ctl.save_bus_servo_deviation(servoId)
            time.sleep(0.01)
            d = self.ctl.get_bus_servo_deviation(servoId)
            if d > 125:
                d = -(0xff-(d - 1))               
            if d != deviation:
                print_err(f'Fail to update servo deviation. Deviation readen from servo:{d}')
                return
            else:
                print('success')       
            
            print(f'ctl.set_bus_servo_temp_limit(id={servoId}, temp={temp})')
            self.ctl.set_bus_servo_temp_limit(servoId, temp)    # update servo tmperature
            time.sleep(0.01)
            d = self.ctl.get_bus_servo_temp_limit(servoId)
            if d != temp:
                print_err(f'Fail to update servo temperature. Temp readen from servo: {d}')
                return
            else:
                print('success')
            
            print(f'set_bus_servo_angle_limit(id={servoId}, pos_min={pos_min}, pos_max={pos_max})')
            self.ctl.set_bus_servo_angle_limit(servoId, (pos_min, pos_max))
            time.sleep(0.01)
            d = self.ctl.get_bus_servo_angle_limit(servoId)
            if d != [pos_min, pos_max]:
                print_err(f'Fail to update pos_min and pos_max. Readen from servo: {d}')
                return
            else:
                print('success')

            print(f'set_bus_servo_vin_limit(id={servoId}, vin_min={vin_min}, vin_max={vin_max})')
            self.ctl.set_bus_servo_vin_limit(servoId, (vin_min, vin_max))
            time.sleep(0.01)
            d = self.ctl.get_bus_servo_vin_limit(servoId)
            if d != [vin_min, vin_max]:
                print_err(f'Fail to update vin_min and vin_max. Readen from servo: {d}')
                return 
            else:
                print('success')

            print(f'set_bus_servo_pulse(id={servoId}, pos={pos}, time={1000}')
            self.ctl.set_bus_servo_pulse(servoId, pos, 1000)   # set servo position

        # ------Move servo--------------------------
        elif name == 'move':
            print(f'move servoId {servoId} to position {pos}')
            if not(1 <= servoId <= MAXSERVOID):
                print_err(f'Invalid servoId parameter: {servoId}')
                return
            if not(0 <= pos <= 1000):
                print_err(f'Invalid pulse parameter: {pos}')
                return
            self.ctl.set_bus_servo_pulse(servoId, pos, 1000)  # 1000ms to move

        # -----Discover all servo----------------
        elif name == 'discover':
            print('Starting servoBus discover command')
            for id in range(1,MAXSERVOID+1):
                print(f'Starting get_bus_servo_deviation: {id}')
                self.deviation = self.ctl.get_bus_servo_deviation(id)
                if self.deviation is not None:
                    if self.deviation > 125:
                        self.deviation = -(0xff-(self.deviation - 1))

                    print('calling get_bus_servo_temp_limit')
                    self.servoTempLimit = self.ctl.get_bus_servo_temp_limit(id)

                    print('calling get_bus_servo_angle_limit')
                    (self.servoMin, self.servoMax) = self.ctl.get_bus_servo_angle_limit(id)

                    print('calling get_bus_servo_vin_limit')
                    (self.servoMinV, self.servoMaxV) = self.ctl.get_bus_servo_vin_limit(id)

                    print('calling get_bus_servo_pulse')
                    self.servoPulse = self.ctl.get_bus_servo_pulse(id)

                    self.discovered_servos_settings[id]= [self.deviation, self.servoTempLimit ,self.servoPulse, self.servoMin,
                                                         self.servoMax, self.servoMinV, self.servoMaxV]
            print(f'Discovered servo count: {len(self.discovered_servos_settings)}')

        # ----Unknown command ------------------
        else:
            print_err(f'Unknown command: {name}')

if __name__ == "__main__": 
    servo = ServoBus()

    currentServoId = -1           # discover servo Id to be updated (only one servo must be connected)
    currentServoId = 1            # force servo Id to be updated
    newServoId = 2                # update current servo Id to new servo id


    if DISCOVER_NEW_AND_SINGLE_SERVO:
        print('---- Reading servo data ----')
        servo.run('read')
    
    if READ_SERVO_DATA_BEFORE_CHANGING_ID:
        print('---- Reading servo data ----')
        servo.run('read', currentServoId)        # The servo Id 1 (default id) must be reconfigured
        time.sleep(1)
        #servo.run('move', currentServoId, pulse=800)

    if RECONFIGURE_ALL_SERVOS:
        for id in range(1,MAXSERVOID+1):
            servo.run('read', id)
            time.sleep(0.1)
            deviation, temp, pos, pos_min, pos_max, vin_min, vin_max = servos_settings[id] # get servo settings from dictionnary
            servo.run('set', id, deviation, temp, pos, pos_min, pos_max, vin_min, vin_max)
            time.sleep(0.1)

    if DISCOVER_ALL_SERVOS:
        print()
        print(f'---- Discover connected servos ----')
        servo.run('discover')
        for id, settings in servo.discovered_servos_settings.items(): 
            print(f"Servo Id : {id}, settings : {settings}")

    if UPDATE_SERVO_ID:
        print()
        print(f'---- Updating servo id from {currentServoId} to {newServoId} ----')
        servo.run('setId', newServoId)
        time.sleep(1)
        print('---- Verify servo data ----')
        servo.run('read', newServoId)
        time.sleep(1)

    if UPDATE_SERVO_CONFIG:
        print()
        print(f'---- Configuring servo {newServoId} ----')
        #servo.run('set', currentServoId, 6, 60, 499, 300, 700, 4600, 13000)
        deviation, temp, pos, pos_min, pos_max, vin_min, vin_max = servos_settings[newServoId] # get servo settings from dictionnary
        servo.run('set', newServoId, deviation, temp, pos, pos_min, pos_max, vin_min, vin_max)
        time.sleep(1)

    if READ_SERVO_DATA_AFTER_CHANGE:
        print()
        print('---- Verify servo data ----')
        servo.run('read', newServoId)

    if MOVE_SERVO:
        print()
        print('Moving new configured servo')
        if (1 <= newServoId <= MAXSERVOID):
            servo.run('move', newServoId, pos=300)
            time.sleep(1)
            servo.run('move', newServoId, pos=500)

