# Head pwm group servo control
#
# head_servo_ctrl_group.py
# Version 1.0

#!/usr/bin/python3
# coding=utf8
import sys
import time
import signal
import threading
import hiwonder.ros_robot_controller_sdk as rrc
import hiwonder.yaml_handle as yaml_handle

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)
    
print('''function: hiwonder raspberry pi expansion board, control multiple PWM servo)
----------------------------------------------------------
Tips:
 * press Ctrl+C to terminate the current program execution. If unsuccessful, please try multiple times!
----------------------------------------------------------
''')

board = rrc.Board()
start = True

servo_data = None

# Load configuration file data
def load_config():
    global lab_data, servo_data
    
    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)

def Stop(signum, frame):
    global start

    start = False
    print('Closed...')


load_config()
x_middle = servo_data['servo2']        # Data from /home/pi/TonyPi/servo_config.yaml
y_middle = 1500


signal.signal(signal.SIGINT, Stop)  # Keystroke Ctrl + C --> generate a signal

if __name__ == '__main__':
    
    while True:
        # Head vertical move down
        # Note: pwm_servo_set_position returns immediately
        # time.sleep must be > time required to execute pwm_servo_set_position
        # pwm_servo_set_position arguments
        #   pwm_servo_set_position(time delay, [[servoId, pulse], [servoId, pulse]])
        board.pwm_servo_set_position(1, [[1, 1100]]) # set servo 1 pulse width to 1100 and runtime to 1000 milliseconds
        time.sleep(1)                                # must be equal or more than the time required to move the servo
        # Head vertical move up
        board.pwm_servo_set_position(3, [[1, 1500]]) # set servo 1 pulse width to 1500 and runtime to 3000 milliseconds
        time.sleep(3)
        # Head horizontal move left
        board.pwm_servo_set_position(1, [[2, 2000]]) # set servo 1 pulse width to 1500 and runtime to 1000 milliseconds
        time.sleep(1)
        # Head move to upper right
        board.pwm_servo_set_position(1, [[1, 1900], [2, 1000]]) # set servo 1 pulse width to 1000, set servo 2 pulse width to 1000, runtime to 1000 milliseconds
        time.sleep(1)
        # Head move to left
        board.pwm_servo_set_position(1, [[1, 1500], [2, 2000]]) # set servo 1 pulse width to 1500, set servo 2 pulse width to 2000, runtime to 1000 milliseconds
        time.sleep(1)
        # back to middle
        board.pwm_servo_set_position(1, [[1, y_middle], [2, x_middle]]) # set servo 1 pulse width to 1500, set servo 2 pulse width to 1500, runtime to 1000 milliseconds     
        time.sleep(1)
        if not start:   # Ctrl+C pressed
            #board.pwm_servo_set_position(1, [[1, 1500], [2, 1500]]) # set servo 1 pulse width to 1500, set servo 2 pulse width to 1500, runtime to 1000 milliseconds
            #time.sleep(1)
            print('End')
            break