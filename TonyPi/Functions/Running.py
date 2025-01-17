#!/usr/bin/python3
# coding=utf8
import sys
import time
import threading

import Functions.KickBall as KickBall
import Functions.Transport as Transport
import Functions.ColorTrack as ColorTrack
import Functions.FaceDetect as FaceDetect
import Functions.lab_adjust as lab_adjust
import Functions.ColorDetect as ColorDetect
import Functions.VisualPatrol as VisualPatrol
import Functions.RemoteControl as RemoteControl
import Functions.ApriltagDetect as ApriltagDetect
import Extend.athletics_course.hurdles as Hurdles
import Extend.athletics_course.stairway as Stairway
import Extend.vision_grab_course.color_classify as ColorClassify

RunningFunc = 0     # Code de la fonction en cours d'exécution (utilisé par TonyPi.py entre autre)
LastHeartbeat = 0   # watchdog
cam = None
open_once = False   # updated by TonyPi.py

# All function must implement the following method:
#   init(), start(), stop(), exit()
#
#   loadFunc --> call <function>.init()
#   startFunc --> call <function>.start()
#   stopFunc --> call <function>.stop()
#   unloadFunc --> call <function>.exit()
#
FUNCTIONS = {
    1: RemoteControl, # remote control
    2: KickBall,      # auto shooting
    3: ColorDetect,   # color recognition
    4: VisualPatrol,  # intelligent line follow
    5: ColorTrack,    # pan-tilt tracking
    6: FaceDetect,    # face recognition
    7: ApriltagDetect,# tag recognition
    8: Transport,     # intelligent transportation
    9: lab_adjust,    # lab threshold adjustment
    10: Hurdles ,     # hurdles
    11: Stairway ,    # go up and down stairs
    12: ColorClassify # color block classification
}


# New function initialization
# Parameters:
#   newf[0]: function code
def loadFunc(newf):
    global RunningFunc
    new_func = newf[0]

    doHeartbeat()

    if new_func < 1 or new_func > 12:
        return (False,  sys._getframe().f_code.co_name + ": Invalid argument")
    else:
        try:
            if RunningFunc > 1:
                FUNCTIONS[RunningFunc].exit()   # Interruption de la fonction en cours
            RunningFunc = newf[0]               # Update RunningFunc
            if not open_once:
                cam.camera_close()
                cam.camera_open()
            FUNCTIONS[RunningFunc].init()       # Init function
        except Exception as e:
            print(e)
    return (True, (RunningFunc,))

# Exit the current running function
def unloadFunc(tmp = ()):
    global RunningFunc
    if RunningFunc != 0:
        FUNCTIONS[RunningFunc].exit()
        RunningFunc = 0
    if not open_once:
        cam.camera_close()
    return (True, (0,))

# Return the current running function code
def getLoadedFunc(newf):
    global RunningFunc
    return (True, (RunningFunc,))

# Return the current running function name
def CurrentEXE():
    global RunningFunc
    return FUNCTIONS[RunningFunc]

# Function to execute has already been loaded (loadFunc) -> start the fucntion
def startFunc(tmp):
    global RunningFunc
    FUNCTIONS[RunningFunc].start()
    return (True, (RunningFunc,))

# Stop the function but do not exit
def stopFunc(tmp):
    global RunningFunc
    FUNCTIONS[RunningFunc].stop()
    return (True, (RunningFunc,))

# Update heartbeat
def doHeartbeat(tmp=()):
    global LastHeartbeat
    LastHeartbeat = time.time() + 7
    return (True, ())

# Watchdog: if doHeartbeat() has not been executed for a long time --> unloadFunc()
def heartbeatTask():
    global LastHeartbeat
    global RunningFunc
    while True:
        try:
            if LastHeartbeat < time.time():
                if RunningFunc != 0:
                    unloadFunc()
            time.sleep(0.1)
        except Exception as e:
            print(e)

        except KeyboardInterrupt:
            break

threading.Thread(target=heartbeatTask, daemon=True).start()
