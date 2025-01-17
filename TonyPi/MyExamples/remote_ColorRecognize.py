# remote_template.py
# Version: 1.0
# Status: tested and validated 2024-12-21
#
# Devices: Laptop, TonyPi
# 
# Template for TonyPi computer vision remote testing
#
# Attention lorsqu'on exécute ce code, on doit être dans le bon répertoire, 
# sinon on ne peut pas charger ../Functions/CameraCalibration/calibration_param
# Prerequisits
#   - In the console: cd .\TonyPi\MyExamples\  because the script load the file ../Functions/CameraCalibration/calibration_param
#
# Note: To stop the application using keyboard, set focus on the python video window (not the console)
#

import cv2
import time
import numpy as np
import requests
import json
import math

DEBUG = False
LAPTOP_TEST = True      # Use laptop web cam on laptop

MAX_AREA = 20           # original value: 200
MIN_TRIGGER_AREA = 20   # original value: 50

def debug_print(s):
    if DEBUG:
        print(s)

# Detected color
range_rgb = {
    'red': (0, 0, 255),
    'black': (0, 0, 0),   
}

# TonyPi RPC server parameters
RPCurl = "http://192.168.1.52:9030/jsonrpc"
headers = {'content-type': 'application/json'}

# Use StreamingURL = 0 to specify the laptop web cam as the video source,
# OR specify the pathname to a video file to read.
StreamingURL = 'http://192.168.1.52:8080/?action=stream?dummy=param.mjpg'

frame_count = 0
no_frame_count = 0
LastHeartbeat = time.time() + 5

# --------------------------------------------------------
# Config files
import yaml
if LAPTOP_TEST:
    lab_file_path = './config_files/lab_config.yaml'
    servo_file_path = './config_files/servo_config.yaml'
else:
    lab_file_path = '/home/pi/TonyPi/lab_config.yaml'
    servo_file_path = '/home/pi/TonyPi/servo_config.yaml'

def get_yaml_data(yaml_file):
    file = open(yaml_file, 'r', encoding='utf-8')
    file_data = file.read()
    file.close()
    
    data = yaml.load(file_data, Loader=yaml.FullLoader)
    return data

def save_yaml_data(data, yaml_file):
    file = open(yaml_file, 'w', encoding='utf-8')
    yaml.dump(data, file)
    file.close()

# --------------------------------------------------------
# Start streaming server on TonyPi
#   Start RemoteControl function (ID = 1) to start the video streaming server. 
#   This starts the MjpgServer.py app and the streaming 
def start_streaming_server():
    print('Starting Streaming server...')
    
    # Invoke RPCServer.py : LoadFunc
    payload = {
        "method": "LoadFunc",
        "params": [1],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(RPCurl, data=json.dumps(payload), headers=headers).json()
    print(f'LoadFunc function: {response["result"]}')

    # Invoke RPCServer.py : StartFunc
    payload = {
        "method": "StartFunc",
        "params": [],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(RPCurl, data=json.dumps(payload), headers=headers).json()
    print(f'StartFunc function: {response["result"]}')

def stop_streaming_server():
    print('Stopping Streaming server...')

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

def heartBeat():
    global LastHeartbeat, frame_count, no_frame_count
    if not LAPTOP_TEST:
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

# --------------------------------------------------------
# Image processing
# find the contour with the maximal area
# Parameter is the list of contour to be compared
#

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def getAreaMaxContour(contours):
    contour_area_temp = 0
    contour_area_max = 0
    areaMaxContour = None

    for c in contours:  # iterate through all contours
        contour_area_temp = math.fabs(cv2.contourArea(c))  # calculate contour area
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > MIN_TRIGGER_AREA:  # only contours with an area greater than 50 are considered valid; the contour with the largest area is used to filter out interference
                areaMaxContour = c

    return areaMaxContour, contour_area_max  # return the contour with the maximal area


lab_data = get_yaml_data(lab_file_path)
size = (320, 240)

def run_imgProcessing(img):
    # Color recognition
    detect_color = 'None'  
    draw_color = range_rgb["black"]	
    
    img_copy = img.copy()
    img_h, img_w = img.shape[:2]

    frame_resize = cv2.resize(img_copy, size, interpolation=cv2.INTER_NEAREST)
    frame_gb = cv2.GaussianBlur(frame_resize, (3, 3), 3)      
    frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # convert the image to the LAB space

    max_area = 0 
    areaMaxContour_max = 0

    frame_mask = cv2.inRange(frame_lab,
                                        (lab_data['red']['min'][0],
                                         lab_data['red']['min'][1],
                                         lab_data['red']['min'][2]),
                                        (lab_data['red']['max'][0],
                                         lab_data['red']['max'][1],
                                         lab_data['red']['max'][2])) # perform bitwise operation to original image and mask
    eroded = cv2.erode(frame_mask, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))   # corrosion
    dilated = cv2.dilate(eroded, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))     # dilation
    contours = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # find out contours

    areaMaxContour, area_max = getAreaMaxContour(contours)  # find out the contour with the maximal area
    if areaMaxContour is not None:
        if area_max > max_area:# find the maximal area
            max_area = area_max
            areaMaxContour_max = areaMaxContour
        else:
            debug_print('!!! area_max <= max_area')
    else:
        debug_print('!!! areaMaxContour is none')
    if max_area > MAX_AREA:  # the maximal area is found
        ((centerX, centerY), radius) = cv2.minEnclosingCircle(areaMaxContour_max)  # get the minimum bounding circumcircle
        centerX = int(map(centerX, 0, size[0], 0, img_w))
        centerY = int(map(centerY, 0, size[1], 0, img_h))
        radius = int(map(radius, 0, size[0], 0, img_w))            

        detect_color = 'red'
        draw_color = range_rgb["red"]

        cv2.putText(img, "Color: " + detect_color, (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, draw_color, 2) # print the recognized color data, format: Color: ***)
        cv2.circle(img, (centerX, centerY), radius, range_rgb["red"], 2) # draw a circle around the recognized color
    else:
        debug_print(f'!!! max_area <={MAX_AREA}')
    return img



# --------------------------------------------------------

if __name__ == '__main__':
    if not LAPTOP_TEST:
        start_streaming_server()
        time.sleep(0.5)

    # Create a video capture object from the VideoCapture Class.
    # Use source = 0 to specify the web cam as the video source, OR
    # specify the pathname to a video file to read, OR
    # the Streaming server URL (StreamingURL)

    #
    if LAPTOP_TEST:
        video_cap = cv2.VideoCapture(0) # local laptop web cam
        print('Starting cv2.VideoCapture(0) - laptop webcam')
    else:
        video_cap = cv2.VideoCapture(StreamingURL)  # source = StreamingURL
        print(f'Starting cv2.VideoCapture({StreamingURL}) - TonyPi camera')

    # Create a named window for the video display.
    win_name = 'Video Preview'
    cv2.namedWindow(win_name)

    # storage path for calibration parameters
    calibration_param_path = '../Functions/CameraCalibration/calibration_param'
    print("Calibration parameters")
    param_data = np.load(calibration_param_path + '.npz')

    mtx = param_data['mtx_array']
    dist = param_data['dist_array']
    debug_print('starting getOptimalNewCameraMatrix')
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (640, 480), 0, (640, 480))
    debug_print('starting initUndistortRectifyMap')
    mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (640, 480), 5)

    # print("starting video_cap.read()")
    # has_frame, img = video_cap.read()
    # frame_w = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # frame_h = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # fps = int(video_cap.get(cv2.CAP_PROP_FPS))
    # print(f'Weidth: {frame_w}, height: {frame_h}, fps: {fps}')

    print("Press q or esc to exit")
    # Enter a while loop to read and display the video frames one at a time.
    while True:
        # Read one frame at a time using the video capture object.
        #print("starting video_cap.read()")
        has_frame, img = video_cap.read()
        if not has_frame:
            print("No frame!")
            no_frame_count += 1
            time.sleep(0.01)
        else:
            frame_count += 1
            #print(frame_count)
            frame = img.copy()
            frame = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR) 
            Frame = run_imgProcessing(frame)    # Run action on frame
            cv2.imshow(win_name, frame)         # Display the current frame in the named window.

        if LastHeartbeat < time.time():
            heartBeat()

        # Use the waitKey() function to monitor the keyboard for user input.
        # key = cv2.waitKey(0) will display the window indefinitely until any key is pressed.
        # key = cv2.waitKey(1) will display the window for 1 ms
        key = cv2.waitKey(1)

        # The return value of the waitKey() function indicates which key was pressed.
        # You can use this feature to check if the user selected the `q` key to quit the video stream.
        if (key == ord('Q')) or (key == ord('q')) or (key == 27) or (frame_count > 1000) or (no_frame_count > 20):
            # Exit the loop.
            print("Exit loop")
            break

    if not LAPTOP_TEST:
        stop_streaming_server()
    video_cap.release()
    cv2.destroyWindow(win_name)
