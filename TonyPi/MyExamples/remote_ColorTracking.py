# remote_ColorTracking.py
# Version: 1.0
# Status: tested and validated 2024-12-20
#
# Devices: TonyPi
# 
# Remotely Call Functions/ColorTrack.py (via RPCServer.py)
# TonyPi head follow the color ball
#
# Prerequisits
#   - run on Windows laptop
#   - In the console: cd .\TonyPi\MyExamples\  because the script load the file ../Functions/CameraCalibration/calibration_param
#
# Note: To stop the application using keyboard, set focus on the python video window (not the console)
#

# 1- remotely start ColorTracking app
# 2- Set color to track (RPC call to SetTargetTrackingColor function)
# 3- start tracking
# 4- get and display streaming vidéo

import cv2
import time
import numpy as np
import requests
import json

RPCurl = "http://192.168.1.52:9030/jsonrpc"
headers = {'content-type': 'application/json'}
StreamingURL = 'http://192.168.1.52:8080/?action=stream?dummy=param.mjpg'

DEBUG = False

def debug_print(s):
    if DEBUG:
        print(s)

def load_ColorTracking_app():
    print('Starting ColorTracking application...')
    
    # Invoke RPCServer.py : LoadFunc
    # 5: ColorTrack,    # pan-tilt tracking
    payload = {
        "method": "LoadFunc",
        "params": [5],      
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(RPCurl, data=json.dumps(payload), headers=headers).json()
    print(f'LoadFunc function: {response["result"]}')

def start_ColorTracking_app():
    # Invoke RPCServer.py : StartFunc
    payload = {
        "method": "StartFunc",
        "params": [],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(RPCurl, data=json.dumps(payload), headers=headers).json()
    print(f'StartFunc function: {response["result"]}')

# Call RCP function SetTargetTrackingColor
def set_trackingColor(color):
    print(f'Set tracking color to {color}')
    payload = {
        "method": "SetTargetTrackingColor",
        "params": [('red',)],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(RPCurl, data=json.dumps(payload), headers=headers).json()
    print(f'set_trackingColor function: {response["result"]}')      

def stop_ColorTracking_app():
    print('Stopping ColorTracking app...')

    # Invoke RPCServer.py : StopFunc
    payload = {
        "method": "StopFunc",
        "params": [],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(RPCurl, data=json.dumps(payload), headers=headers).json()
    print(f'StopFunc function: {response["result"]}')

    # Invoke RPCServer.py : FinishFunc
    payload = {
        "method": "UnloadFunc",
        "params": [],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(RPCurl, data=json.dumps(payload), headers=headers).json()
    print(f'UnloadFunc function: {response["result"]}')

# run every 5 sec
def heartBeat():
    global LastHeartbeat, frame_count, no_frame_count
    payload = {
        "method": "Heartbeat",
        "params": [],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(RPCurl, data=json.dumps(payload), headers=headers).json()
    debug_print(f'doHeartbeat function: {response}')
    LastHeartbeat = time.time() + 5
    print(f'frame: {frame_count} - no frame: {no_frame_count}')

# --------------------------------------------------------------
if __name__ == '__main__':
    load_ColorTracking_app()
    LastHeartbeat = time.time() + 5
    #set_trackingColor('red')
    start_ColorTracking_app()

    print(f'Starting cv2.VideoCapture({StreamingURL})')
    video_cap = cv2.VideoCapture(StreamingURL)  # source = StreamingURL
                                                # Le streaming reçu est le résultat du traitement de l'image 
                                                # par la function qu'on vient juste de démarrer (ci-dessus)
    # Create a named window for the video display.
    win_name = 'Video Preview'
    cv2.namedWindow(win_name)
    frame_count = 0
    no_frame_count = 0

    # storage path for calibration parameters
    # calibration_param_path = '../Functions/CameraCalibration/calibration_param'
    # print("Calibration parameters")
    # param_data = np.load(calibration_param_path + '.npz')

    # mtx = param_data['mtx_array']
    # dist = param_data['dist_array']
    # print('starting getOptimalNewCameraMatrix')
    # newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (640, 480), 0, (640, 480))
    # print('starting initUndistortRectifyMap')
    # mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (640, 480), 5)

    print("starting video_cap.read()")
    print("Press q or esc to exit")
    # Enter a while loop to read and display the video frames one at a time.
    while True:
        # Read one frame at a time using the video capture object.
        has_frame, img = video_cap.read()
        if not has_frame:
            print("No frame!")
            no_frame_count += 1
            time.sleep(0.01)
        else:
            frame_count += 1
            debug_print(frame_count)
            #frame = img.copy()
            #frame = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)  
            #Frame = run(frame)     # Run action on frame (already done in TonyPi.py -> ColorTracking.py app)
            cv2.imshow(win_name, img) # Display the current frame in the named window.

        # Use the waitKey() function to monitor the keyboard for user input.
        # key = cv2.waitKey(0) will display the window indefinitely until any key is pressed.
        # key = cv2.waitKey(1) will display the window for 1 ms
        key = cv2.waitKey(1)

        if LastHeartbeat < time.time():
            heartBeat()

        # The return value of the waitKey() function indicates which key was pressed.
        # You can use this feature to check if the user selected the `q` key to quit the video stream.
        if (key == ord('Q')) or (key == ord('q')) or (key == 27) or (frame_count > 1000) or (no_frame_count > 20):
            # Exit the loop.
            print("Exit loop")
            stop_ColorTracking_app()
            break

    video_cap.release()
    cv2.destroyWindow(win_name)