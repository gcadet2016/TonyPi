# TonyPi/MyExamples/servos/bus_servos_read.py
# Testé le 2024-12-23
#
# Run on TonyPi 
#
# Same result than bus_servo_read_debug.py but invoke SDK as a normal application 
# Get info from the first servo (should be used when only one servo is connected) whatever is its id

import sys
import time
import signal
import threading
import ros_robot_controller_sdk as rrc

print('''
--------------------------------------------------------------------------
function: hiwonder raspberry pi expansion board, read the bus servo's data

Official website:https://www.hiwonder.com
Online mall:https://hiwonder.tmall.com

Tips: 
      press Ctrl+C to terminate the current program execution. 
      If unsuccessful, please try multiple times! (ca pue le bug)
--------------------------------------------------------------------------
''')
board = rrc.Board()
board.enable_reception()
start = True

# process before closing
def Stop(signum, frame):
    global start
    start = False
    print('Exit...')

signal.signal(signal.SIGINT, Stop)

# Get servo informations
def bus_servo_test(board):
    servo_id = board.bus_servo_read_id()    # Invoke rcc.Board to get all servo ids 
    print(servo_id)
    if servo_id is not None:
        servoID = servo_id[0]
        vin =  board.bus_servo_read_vin(servoID)
        temp = board.bus_servo_read_temp(servoID)
        position = board.bus_servo_read_position(servoID)
        # Output servo state
        print("id:", servoID)
        print('vin:', vin)
        print('temp:',temp)
        print('position',position)
    else:
        print('No response - servo_id is none')

if __name__ == '__main__':
    try:
        while start:
            bus_servo_test(board)
            time.sleep(1)
    except KeyboardInterrupt:
        print('Ctrl+C received')
