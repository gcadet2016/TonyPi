# board_imu_demo.py
# V1.1
# Tested 20025-01-25
#
# Bug fixed: add time.sleep(1) after enable_reception() to avoid 'Sensor not connected!' error
#
import time
import ros_robot_controller_sdk as rrc
import numpy as np
import math

'''
    Program function: IMU routine(MPU6050)
    Running effect: after the program runs, the IMU data is continuously outputted on the screen

    Corresponding tutorial file path:TonyPi Intelligent Vision Humanoid Robot\4. Expanded Courses\5. Raspberry Pi Expansion Board\Lesson 7 The Use of Accelerometer)
'''

def calculate_orientation(accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, dt):
    # Full scale range +/- 250 degree/C as per sensitivity scale factor
    accel_x = accel_x / 16384.0
    accel_y = accel_y / 16384.0
    accel_z = accel_z / 16384.0
    gyro_x = gyro_x / 131.0
    gyro_y = gyro_y / 131.0
    gyro_z = gyro_z / 131.0

    roll1 = np.arctan2(accel_y, accel_z) * 180 / np.pi
    roll2 = np.arctan2(accel_y, accel_x) * 180 / np.pi
    pitch1 = np.arctan2(-accel_x, np.sqrt(accel_y**2 + accel_z**2)) * 180 / np.pi
    # yaw = gyro_z * dt

    # Calculate pitch, roll, and yaw
    pitch = math.atan2(accel_y, math.sqrt(accel_x * accel_x + accel_z * accel_z)) * 180 / math.pi
    roll = math.atan2(-accel_x, accel_z) * 180 / math.pi
    yaw = math.atan2(accel_z, math.sqrt(accel_x * accel_x + accel_y * accel_y)) * 180 / math.pi

    return yaw, pitch, roll, pitch1, roll1, roll2

board = rrc.Board()
board.enable_reception()
time.sleep(1)

prev_time = time.time()
while True:
    try:
        accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z = board.get_imu()           # Get IMU data
        print(f'accel_x:{accel_x:.2f}, accel_y:{accel_y:.2f}, accel_z:{accel_z:.2f}')
        print(f'gyro_x :{gyro_x:.2f}, gyro_y :{gyro_y:.2f}, gyro_z :{gyro_z:.2f}')

        current_time = time.time()
        dt = current_time - prev_time
        prev_time = current_time

        yaw, pitch, roll, p1, r1, r2 = calculate_orientation(accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, dt)
        print(f"Yaw: {yaw:.2f}, Pitch: {pitch:.2f}, Roll: {roll:.2f}") #, p1: {p1:.2f}, r1: {r1:.2f}, r2: {r2:.2f}")

        time.sleep(0.1)

        # while True:
        #     try:
        #         res = board.get_imu()           # Get IMU data
        #         if res is not None:
        #             print(res)                  # ouput the obtained IMU data
                
        #         time.sleep(1)
    except KeyboardInterrupt:
        break
