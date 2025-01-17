#!/usr/bin/python3
# coding=utf8
import sys
import os
import cv2
import time
import queue
import logging
import threading
import RPCServer
import MjpgServer
import numpy as np

import hiwonder.Camera as Camera
import hiwonder.yaml_handle as yaml_handle

import Functions.Running as Running

# the main thread is already set to start in the background upon boot
# the autostart method is systemd, with the autostart file located at /etc/systemd/system/tonypi.service
# sudo systemctl stop tonypi  (closing this time)
# sudo systemctl disable tonypi (permanently close)
# sudo systemctl enable tonypi (permanently open)
# sudo systemctl start tonypi (open this time)

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

QUEUE_RPC = queue.Queue(10)

def startTonyPi():

    RPCServer.QUEUE = QUEUE_RPC

    threading.Thread(target=RPCServer.startRPCServer,
                     daemon=True).start()  # rpc server
    threading.Thread(target=MjpgServer.startMjpgServer,
                     daemon=True).start()  # mjpg stream server
    
    
    loading_picture = cv2.imread('/home/pi/TonyPi/Functions/loading.jpg')
    cam = Camera.Camera()  # 相机读取(camera reading)
    open_once = yaml_handle.get_yaml_data('/boot/camera_setting.yaml')['open_once']
    if open_once:
        cam.camera_open()

    open_once
    Running.open_once = open_once
    Running.cam = cam

    while True:
        time.sleep(0.03)
        # execute RPC commands that need to be executed in this thread
        # RPC command has been enqueued by RPCSever.py
        while True:
            try:
                req, ret = QUEUE_RPC.get(False) # req = proc name to run (PC command),  
                                                # ret = (event, parameters, result)
                                                # arg:False -> raise the Empty exception if QUEUE is empty
                event, params, *_ = ret     # *_ = et tout le reste - The preferred way to discard values is to use an underscore variable (_)
                ret[2] = req(params)        # execute RPC command
                event.set()
            except:
                break   # Exit when QUEUE is empty
        #####
        # perform function program
        try:
            if Running.RunningFunc > 0 and Running.RunningFunc <= 12:
                if cam.frame is not None:
                    # Une frame fournie par la caméra --> lancer la function de traitement 
                    img = Running.CurrentEXE().run(cam.frame.copy())    # Invoke run(img) of the current running function
                    if Running.RunningFunc == 9:
                        MjpgServer.img_show = np.vstack((img, cam.frame))
                    else:
                        MjpgServer.img_show = img
                else:
                    # pas d'image de caméra
                    MjpgServer.img_show = loading_picture
            else:
                if open_once:
                    MjpgServer.img_show = cam.frame
                else:
                    cam.frame = None
        except KeyboardInterrupt:
            break
        except BaseException as e:
            print('error', e)

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    startTonyPi()
