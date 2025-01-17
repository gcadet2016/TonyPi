import sys
import time
import signal
import threading
import ros_robot_controller_sdk as rrc

print('''
**********************************************************
******** function: hiwonder raspberry pi expansion board, control the bus servo's rotation**********
**********************************************************
----------------------------------------------------------
Official website:https://www.hiwonder.com
Online mall:https://hiwonder.tmall.com
----------------------------------------------------------
Tips:
 * press Ctrl+C to terminate the current program execution. If unsuccessful, please try multiple times!
----------------------------------------------------------
''')
board = rrc.Board()
start = True

# process before closing
def Stop(signum, frame):
    global start
    start = False
    print('Exit...')

signal.signal(signal.SIGINT, Stop)

if __name__ == '__main__':
    while True:
        board.bus_servo_set_position(1, [[1, 500], [2, 500]])
        time.sleep(1)
        board.bus_servo_set_position(2, [[1, 510], [2, 510]])
        time.sleep(1)
        board.bus_servo_stop([1, 2])
        time.sleep(1)
        if not start:
            board.bus_servo_stop([1, 2])
            time.sleep(1)
            print('Fin')
            break