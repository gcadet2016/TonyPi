# Non testé
import ros_robot_controller_sdk as rrc
import math
import time

board = rrc.Board()
board.enable_reception()
time.sleep(1)

def read_raw_data(addr):
    # Accelero and Gyro values are 16-bit
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr + 1)
    
    # Concatenate higher and lower value
    value = ((high << 8) | low)
    
    # Get signed value from mpu6050
    if value > 32768:
        value = value - 65536
    return value

def get_pitch_roll_yaw():
    # Read Accelerometer raw value
    acc_x = read_raw_data(ACCEL_XOUT_H)
    acc_y = read_raw_data(ACCEL_YOUT_H)
    acc_z = read_raw_data(ACCEL_ZOUT_H)
    
    # Read Gyroscope raw value
    gyro_x = read_raw_data(GYRO_XOUT_H)
    gyro_y = read_raw_data(GYRO_YOUT_H)
    gyro_z = read_raw_data(GYRO_ZOUT_H)
    
    # Full scale range +/- 250 degree/C as per sensitivity scale factor
    Ax = acc_x / 16384.0
    Ay = acc_y / 16384.0
    Az = acc_z / 16384.0
    
    Gx = gyro_x / 131.0
    Gy = gyro_y / 131.0
    Gz = gyro_z / 131.0
    
    # Calculate pitch, roll, and yaw
    pitch = math.atan2(Ay, math.sqrt(Ax * Ax + Az * Az)) * 180 / math.pi
    roll = math.atan2(-Ax, Az) * 180 / math.pi
    yaw = math.atan2(Az, math.sqrt(Ax * Ax + Ay * Ay)) * 180 / math.pi
    
    return pitch, roll, yaw

# Initialize MPU6050
MPU_Init()

print("Reading Data from MPU6050")

while True:
    pitch, roll, yaw = get_pitch_roll_yaw()
    
    print(f"Pitch: {pitch:.2f}, Roll: {roll:.2f}, Yaw: {yaw:.2f}")
    time.sleep(1)
