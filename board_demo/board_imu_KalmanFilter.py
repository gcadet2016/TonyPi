# Non testé
# A adapter
# Source: 
import smbus2
import time
import numpy as np
from filterpy.kalman import KalmanFilter

# Adresse I2C du MPU6050
MPU6050_ADDR = 0x68

# Registres du MPU6050
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

# Initialiser le bus I2C
bus = smbus2.SMBus(1)

# Activer le MPU6050
bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)

def read_word(bus, addr, reg):
    high = bus.read_byte_data(addr, reg)
    low = bus.read_byte_data(addr, reg + 1)
    val = (high << 8) + low
    if val >= 0x8000:
        return -((65535 - val) + 1)
    else:
        return val

def read_mpu6050(bus, addr):
    accel_x = read_word(bus, addr, ACCEL_XOUT_H)
    accel_y = read_word(bus, addr, ACCEL_XOUT_H + 2)
    accel_z = read_word(bus, addr, ACCEL_XOUT_H + 4)
    gyro_x = read_word(bus, addr, GYRO_XOUT_H)
    gyro_y = read_word(bus, addr, GYRO_XOUT_H + 2)
    gyro_z = read_word(bus, addr, GYRO_XOUT_H + 4)
    return accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z

# Initialiser le filtre de Kalman
def create_kalman_filter():
    kf = KalmanFilter(dim_x=2, dim_z=1)
    kf.x = np.array([0, 0])  # état initial
    kf.F = np.array([[1, 1], [0, 1]])  # matrice de transition
    kf.H = np.array([[1, 0]])  # matrice d'observation
    kf.P *= 1000  # incertitude initiale
    kf.R = 5  # bruit de mesure
    kf.Q = np.eye(2)  # bruit de processus
    return kf

kalman_filters = [create_kalman_filter() for _ in range(6)]  # 6 axes (accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z)

# Fonction pour appliquer le filtre de Kalman
def apply_kalman_filter(kf, measurement):
    kf.predict()
    kf.update(measurement)
    return kf.x[0]

while True:
    accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z = read_mpu6050(bus, MPU6050_ADDR)
    measurements = [accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z]
    filtered_measurements = [apply_kalman_filter(kf, m) for kf, m in zip(kalman_filters, measurements)]
    print("Filtered Measurements:", filtered_measurements)
    time.sleep(0.1)
