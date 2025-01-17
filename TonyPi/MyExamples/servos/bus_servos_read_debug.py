# TonyPi/MyExamples/servos/bus_servos_read_debug.py
# Testé le 2024-12-23
#
# Run on TonyPi 
#
# Same result than bus_servo_read.py but code has been copied locally from sdk in this file to avoid call to Controller.py
# and debug SDK
# Features:
#   Get info from the first servo (should be used when only one servo is connected) whatever is its id
#   Get info from all servos (should be used when only one servo is connected) whatever is its id

import sys
import time
import signal
import threading
import ros_robot_controller_sdk as rrc
import queue
import struct
import serial
import cv2

print('''
---------------------------------------------------------------------------
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
running = True
time_out = 10

# process before closing
# def Stop(signum, frame):
#     global start
#     start = False
#     print('Exit...')

# signal.signal(signal.SIGINT, Stop)

servo_read_lock = threading.Lock()
PACKET_FUNC_BUS_SERVO = 5  # bus servo control
bus_servo_queue = queue.Queue(maxsize=1)
crc8_table = [
    0, 94, 188, 226, 97, 63, 221, 131, 194, 156, 126, 32, 163, 253, 31, 65,
    157, 195, 33, 127, 252, 162, 64, 30, 95, 1, 227, 189, 62, 96, 130, 220,
    35, 125, 159, 193, 66, 28, 254, 160, 225, 191, 93, 3, 128, 222, 60, 98,
    190, 224, 2, 92, 223, 129, 99, 61, 124, 34, 192, 158, 29, 67, 161, 255,
    70, 24, 250, 164, 39, 121, 155, 197, 132, 218, 56, 102, 229, 187, 89, 7,
    219, 133, 103, 57, 186, 228, 6, 88, 25, 71, 165, 251, 120, 38, 196, 154,
    101, 59, 217, 135, 4, 90, 184, 230, 167, 249, 27, 69, 198, 152, 122, 36,
    248, 166, 68, 26, 153, 199, 37, 123, 58, 100, 134, 216, 91, 5, 231, 185,
    140, 210, 48, 110, 237, 179, 81, 15, 78, 16, 242, 172, 47, 113, 147, 205,
    17, 79, 173, 243, 112, 46, 204, 146, 211, 141, 111, 49, 178, 236, 14, 80,
    175, 241, 19, 77, 206, 144, 114, 44, 109, 51, 209, 143, 12, 82, 176, 238,
    50, 108, 142, 208, 83, 13, 239, 177, 240, 174, 76, 18, 145, 207, 45, 115,
    202, 148, 118, 40, 171, 245, 23, 73, 8, 86, 180, 234, 105, 55, 213, 139,
    87, 9, 235, 181, 54, 104, 138, 212, 149, 203, 41, 119, 244, 170, 72, 22,
    233, 183, 85, 11, 136, 214, 52, 106, 43, 117, 151, 201, 74, 20, 246, 168,
    116, 42, 200, 150, 21, 75, 169, 247, 182, 232, 10, 84, 215, 137, 107, 53
]
device="/dev/ttyAMA0"
baudrate=1000000
timeout=5
port = serial.Serial(None, baudrate, timeout=timeout)
port.rts = False
port.dtr = False
port.setPort(device)
port.open()

# code from ros_robot_controller_sdk.py
def checksum_crc8(data):
    check = 0
    for b in data:
        check = crc8_table[check ^ b]
    return check & 0x00FF

# code from ros_robot_controller_sdk.py
def buf_write(func, data):
    global port
    print(f'Starting buf_write func= {func}, data= {data}')
    buf = [0xAA, 0x55, int(func)]
    buf.append(len(data))
    buf.extend(data)
    buf.append(checksum_crc8(bytes(buf[2:])))
    port.write(buf)

# code from ros_robot_controller_sdk.py
def bus_servo_read_and_unpack(servo_id, cmd, unpack):
    print(f'Starting bus_servo_read_and_unpack cmd= {cmd}, servo_id= {servo_id}, unpack= {unpack}')
    with servo_read_lock:
        buf_write(PACKET_FUNC_BUS_SERVO, [cmd, servo_id])
        data = bus_servo_queue.get(block=True)
        print(data)
        servo_id, cmd, success, *info = struct.unpack(unpack, data)
        if success == 0:
            return info
        else:
            print(f'Error: servo_id= {servo_id}, cmd= {cmd}, success= {success}, info= {info}')

# code from ros_robot_controller_sdk.py
def bus_servo_read_id(servo_id=254):
        return bus_servo_read_and_unpack(servo_id, 0x12, "<BBbB")

# code from controller.py
# return an int = first servoId in the list (return data[0])
def get_bus_servo_id():
    count = 0
    while True:
        data = board.bus_servo_read_id()
        count += 1
        if data is not None:
            return data[0]
        if count > time_out:
            print('get_bus_servo_id timeout!')
            return None
        time.sleep(0.01)

def get_bus_servo_id_list():
    count = 0
    while True:
        data = board.bus_servo_read_id()
        count += 1
        if data is not None:
            return data
        if count > time_out:
            print('get_bus_servo_id timeout!')
            return None
        time.sleep(0.01)

# def get_bus_servo_vin_limit(servo_id):
#     count = 0
#     while True:
#         data = board.bus_servo_read_vin_limit(servo_id)
#         count += 1
#         if data is not None:
#             print(f'get_bus_servo_vin_limit: data= {data}')
#             return data
#         if count > time_out:
#             return None
#         time.sleep(0.01)

def print_servo_settings(servo_id):
            # Do not invoke Controller.py, directly invoke rcc.Board
        vin =  board.bus_servo_read_vin(servo_id)
        temp = board.bus_servo_read_temp(servo_id)
        position = board.bus_servo_read_position(servo_id)
        angle_limits = board.bus_servo_read_angle_limit(servo_id)
        vin_limits = board.bus_servo_read_vin_limit(servo_id)
        # Output servo state
        print("id:", servo_id)
        print('vin:', vin)
        print('temp:',temp)
        print('position:',position)
        print('angle limits:',angle_limits)
        print('vin limits:',vin_limits)
        print('------------------------')

# Get servo informations
def bus_servo_read_1(board):
    #servo_id = bus_servo_read_id()
    servo_id = get_bus_servo_id()
    print(servo_id)
    if servo_id is not None:
        print_servo_settings(servo_id)
    else:
        print('No response - servo_id is none')

def bus_servo_read_all(board):
    global running
    print('Starting bus_servo_read_all')
    servo_id_list = board.bus_servo_read_id()    # Invoke rcc.Board to get all servo ids
    print(servo_id_list)
    if servo_id_list is not None:
        for servo_id in servo_id_list:
            print_servo_settings(servo_id)
    running = False

if __name__ == '__main__':
    try:
        while running:
            #bus_servo_read_1(board)       # read the servo id of a a single connected servo
            bus_servo_read_all(board)      # read the servo id of all connected servo
            time.sleep(1)
            key = cv2.waitKey(1)            # ne fonctionne pas :-(
            if (key == ord('Q')) or (key == ord('q')) or (key == 27):
                print("Exit")
                break
    except KeyboardInterrupt:
        print('Ctrl+C received')
