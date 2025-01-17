# Camera_thread.py
# V1.0
# Class Camera: Initialize the camera and obtain the image from the camera
# Thread is used in this version
#
# Prerequisits: cd .\TonyPi\MyExamples\body\ 
#               Set LAPTOP = True for laptop camera
#
# Tested on laptop : 2024-01-06
# Tested on TonyPi : 
#
#!/usr/bin/env python3
# encoding:utf-8
import sys
import cv2
import time
import threading
import numpy as np

import yaml_handle
# if __name__ == '__main__':
#     import yaml_handle
# else:
#     from . import yaml_handle

# this is a wrapper library for obtaining video from a USB camera using OpenCV
LAPTOP = True       # LAPTOP = True to use laptop camera
#LAPTOP = False     # LAPTOP = False for TonyPi camera

if LAPTOP:
    CAMERA_SETTINGS_PATH = '..\\..\\..\\boot\\camera_setting.yaml'
    CAMERA_ID = 0
else:
    CAMERA_SETTINGS_PATH = '/boot/camera_setting.yaml'
    CAMERA_ID = -1

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

class Camera():
    def __init__(self, CameraID=0, CameraSettingsPath='camera_setting.yaml', resolution=(640, 480)):
        self.CameraID = CameraID
        self.CameraSettingsPath = CameraSettingsPath
        self.cap = None
        self.width = resolution[0]
        self.height = resolution[1]
        self.frame = None
        self.opened = False
        
        camera_setting = yaml_handle.get_yaml_data(self.CameraSettingsPath)
        self.flip = camera_setting['flip']
        self.flip_param = camera_setting['flip_param']

        # obtain a image in the sub-thread form
        self.th = threading.Thread(target=self.camera_task, args=(), daemon=True)
        self.th.start()

    def camera_open(self): 
        try:
            #self.cap = cv2.VideoCapture(self.CameraID)
            self.cap = cv2.VideoCapture(0)
            if not LAPTOP:
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V'))
            self.cap.set(cv2.CAP_PROP_FPS, 30)          # frame rate
            #self.cap.set(cv2.CAP_PROP_SATURATION, 40)   # saturation
            self.opened = True
        except Exception as e:
            print('Error:', e)

    def camera_close(self): 
        try:
            self.opened = False
            time.sleep(0.2)
            if self.cap is not None:
                self.cap.release()
                time.sleep(0.05)
            self.cap = None
        except Exception as e:
            print('Error:', e)

    def isOpened(self):
        return self.cap.isOpened()

    def read(self):
        if self.frame is None:
            return False, self.frame
        else:
            return True, self.frame
    
    def camera_task(self): # get camera image thread
        while True:
            try:
                if self.opened and self.cap.isOpened(): # determine whether it is opened
                    ret, frame_tmp = self.cap.read() # get image
                    if ret:
                        if self.flip:
                            Frame = cv2.resize(frame_tmp, (self.width, self.height), interpolation=cv2.INTER_NEAREST) # scaling
                            self.frame = cv2.flip(Frame, self.flip_param)
                        else:
                            self.frame = cv2.resize(frame_tmp, (self.width, self.height), interpolation=cv2.INTER_NEAREST) # scaling
                    else:
                        # if obtaining the image fails, attempt to reopen the camera
                        # print('Fail to get image, reopen the camera')
                        self.frame = None
                        # cap = cv2.VideoCapture(self.CameraID)
                        # ret, _ = cap.read()
                        # if ret:
                        #     self.cap = cap
                # elif self.opened:
                #     print('self.cap.isOpened() is False, reopen the camera')
                #     cap = cv2.VideoCapture(self.CameraID)
                #     ret, _ = cap.read()
                #     if ret:
                #         self.cap = cap              
                else:
                    time.sleep(0.01)
            except Exception as e:
                print('Error:', e)
                time.sleep(0.01)


if __name__ == '__main__':
    # usage routine
    my_camera = Camera(CameraID=CAMERA_ID, CameraSettingsPath=CAMERA_SETTINGS_PATH)
    my_camera.camera_open()
    print(f'Camera ID: {my_camera.CameraID}')
    print(f'Camera settings path: {my_camera.CameraSettingsPath}')
    print(f'Camera opened: {my_camera.opened} & {my_camera.cap.isOpened()}')

    print("L’image d’origine de l’appareil photo n’a pas été corrigée pour la distorsion")
    print('Press ESC to exit')
    time.sleep(1)
    while True:
        # Il y a un thread qui s'occupe de la capture d'image, donc on peut directement lire l'image
        img = my_camera.frame
        if img is not None:
            cv2.imshow('img', img)
            key = cv2.waitKey(1)
            if key == 27:
                break  
    my_camera.camera_close()
    cv2.destroyAllWindows()
