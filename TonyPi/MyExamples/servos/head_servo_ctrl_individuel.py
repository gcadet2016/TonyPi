# Head servo individual pwm control
#
# head_servo_ctrl_individuel.py
# Version: 1.0
#
# /home/pi/TonyPi/servo_config.yaml content (à priori ce n'est pas du yaml !)
#   servo1: 1005
#   servo2: 1417        

import time
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller
import hiwonder.yaml_handle as yaml_handle

board = rrc.Board()
ctl = Controller(board)

servo_data = None

# Load configuration file data
def load_config():
    global lab_data, servo_data
    
    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)

load_config()

x_dis = servo_data['servo2']        # Data from /home/pi/TonyPi/servo_config.yaml
y_dis = 1500

ctl.set_pwm_servo_pulse(1, 1900, 500)   # move head up
ctl.set_pwm_servo_pulse(2, 1100, 500)   # move head right
time.sleep(1)
ctl.set_pwm_servo_pulse(1, y_dis, 500)   # move head up
ctl.set_pwm_servo_pulse(2, x_dis, 500)   # move head right