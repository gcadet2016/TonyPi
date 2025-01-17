#!/usr/bin/env python3
# encoding:utf-8
import os
import cv2
from CalibrationConfig import *
import hiwonder.Camera as Camera
import hiwonder.yaml_handle as yaml_handle

# collect calibration images, save them in the 'calib' folder
# Press the space key on the keyboard to save the image, press esc to exit
open_once = yaml_handle.get_yaml_data('/boot/camera_setting.yaml')['open_once']
if open_once:
    cap = cv2.VideoCapture('http://127.0.0.1:8080/?action=stream?dummy=param.mjpg')
else:
    cap = Camera.Camera()
    cap.camera_open() 

# if the 'calib' folder does not exist, create it
if not os.path.exists(save_path):                   # save_path defined in CalibrationConfig.py
    os.mkdir(save_path)

# Calculate the number of stored images
num = 0
while True:
    ret, frame = cap.read()
    if ret:
        Frame = frame.copy()
        cv2.putText(Frame, str(num), (10, 50), cv2.FONT_HERSHEY_COMPLEX, 2.0, (0, 0, 255), 5)
        cv2.imshow("Frame", Frame)
        key = cv2.waitKey(1)
        if key == 27:
            break
        if key == 32:
            num += 1
            # The image name format: current image number.jpg
            cv2.imwrite(save_path + str(num) + ".jpg", frame) 

cap.release()
cv2.destroyAllWindows()