# Motion_detection.py
# Version: 1.0
# Status: tested and validated 2024-12-17
#
# Prerequisits
#   - run on Windows laptop
#   - In the console: cd .\TonyPi\MyExamples\  because the script load the file ../Functions/CameraCalibration/calibration_param
#
# Note: To stop the application using keyboard, set focus on the python video window (not the console)
#
# Known issues:
# StreamingURL = 'http://192.168.1.52:8080/?action=stream?dummy=param.mjpg'
# Error: [ WARN:0@30.081] global cap_ffmpeg_impl.hpp:453 _opencv_ffmpeg_interrupt_callback Stream timeout triggered after 30079.669000 ms
# Cause: Streaming server not started on TonyPi

import cv2
import time
import numpy as np
import requests
import json
import PID

LAPTOP_TEST = True      # Use laptop web cam on laptop
DEBUG = False
THRESHOLD = 100
HEAD_MOVE = False

# global var
# Process video.
ksize = (5, 5)
red = (0, 0, 255)
yellow = (0, 255, 255)
green = (0, 255, 0)

def debug_print(s):
    if DEBUG:
        print(s)

# Use source = 0 to specify the web cam as the video source, OR
# specify the pathname to a video file to read.

### Attention lorsqu'on exécute ce code, on doit être dans le bon répertoire, 
### sinon on ne peut pas charger ../Functions/CameraCalibration/calibration_param
RPCurl = "http://192.168.1.52:9030/jsonrpc"
headers = {'content-type': 'application/json'}

# ---------------------------------------------------------
StreamingURL = 'http://192.168.1.52:8080/?action=stream?dummy=param.mjpg'

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

# ---------------------------------------------------------
# Image processing
# Convenience function for annotating video frames.
def drawBannerText(frame, text, banner_height_percent = 0.08, font_scale = 0.8, text_color = green, font_thickness = 1):
    # Draw a black filled banner across the top of the image frame.
    # percent: set the banner height as a percentage of the frame height.
    banner_height = int(banner_height_percent * frame.shape[0])
    cv2.rectangle(frame, (0, 0), (frame.shape[1], banner_height), (0, 0, 0), 
    	thickness = -1)

    # Draw text on banner.
    left_offset = 20
    location = (left_offset, int(10 + (banner_height_percent * frame.shape[0]) / 2))
    cv2.putText(frame, text, location, cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
    
def img_processing(frame):
    global ksize, red, yellow, x_dis, y_dis

    debug_print('starting img_processing')
    # Motion area based on foreground mask (with erosion)
    fg_mask = bg_sub.apply(frame)
    fg_mask_erode = cv2.erode(fg_mask, np.ones(ksize, np.uint8))
    if cv2.hasNonZero(fg_mask_erode):
        drawBannerText(frame,"Motion detected")

    debug_print('starting findNonZero')
    motion_area_erode = cv2.findNonZero(fg_mask_erode)
    x, y, w, h = cv2.boundingRect(motion_area_erode)
    centerX = x + w/2
    centerY = y + h/2
    cv2.circle(frame, (int(centerX), int(centerY)), 5, green, 1)
    # Draw bounding box for motion area based on foreground mask
    if motion_area_erode is not None:
        cv2.rectangle(frame, (x, y), (x + w, y + h), red, thickness = 2)

    # Robot head (camera) move
    if (not LAPTOP_TEST) and HEAD_MOVE:
        debug_print('starting servo update')
        img_h, img_w = frame.shape[:2]

        use_time = 0    
        
        if abs(centerX - img_w/2.0) < THRESHOLD: #if the movement amplitude  is small, then no need to move
            centerX = img_w/2.0

        x_pid.SetPoint = img_w/2 # set
        x_pid.update(centerX) # current
        dx = int(x_pid.output)
        use_time = abs(dx*0.00025)
        x_dis += dx # output
        
        x_dis = 500 if x_dis < 500 else x_dis          
        x_dis = 2500 if x_dis > 2500 else x_dis

        if abs(centerY - img_h/2.0) < THRESHOLD: # if the movement amplitude is small, then no need to move
            centerY = img_h/2.0  
       
        y_pid.SetPoint = img_h/2
        y_pid.update(centerY)
        dy = int(y_pid.output)
        
        use_time = round(max(use_time, abs(dy*0.00025)), 5)
        
        y_dis += dy
        
        y_dis = 1000 if y_dis < 1000 else y_dis
        y_dis = 2000 if y_dis > 2000 else y_dis    

        setPWMServo(x_dis, y_dis, use_time)

    return frame

# --------------------------------------------------------
# head servo motors remote control
# Arguments: pulseS1 = vertical , pulseS2 = horizontal
x_dis = 1500
y_dis = 1500
x_pid = PID.PID(P=0.145, I=0.00, D=0.0007)  # pid initialization
y_pid = PID.PID(P=0.145, I=0.00, D=0.0007)

def reset_servos():
    global x_dis, y_dis, x_pid, y_pid
    x_dis = 1500
    y_dis = 1500
    x_pid.clear()
    y_pid.clear()
    setPWMServo(x_dis,y_dis)

def setPWMServo(pulseS2, pulseS1, t=1):
    # Invoke RPCServer.py : SetPWMServo
    payload = {
        "method": "SetPWMServo",
        "params": [t*1000, 2, 1, pulseS1, 2, pulseS2],
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(RPCurl, data=json.dumps(payload), headers=headers).json()
    print(f'SetPWMServo function: {response["result"]}')

# --------------------------------------------------------
if __name__ == '__main__':
    if not LAPTOP_TEST:
        start_streaming_server()
        time.sleep(0.5)
        LastHeartbeat = time.time() + 5
        reset_servos()

    # Create background subtraction object.
    bg_sub = cv2.createBackgroundSubtractorKNN (history = 200)

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
    frame_count = 0
    no_frame_count = 0

    # storage path for calibration parameters
    calibration_param_path = '../Functions/CameraCalibration/calibration_param'
    print("Calibration parameters")
    param_data = np.load(calibration_param_path + '.npz')
    debug_print(param_data)

    mtx = param_data['mtx_array']   # Matrice de caméra et coefficients de distorsion obtenus après calibration
    dist = param_data['dist_array']
    print('starting getOptimalNewCameraMatrix')
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (640, 480), 0, (640, 480)) # Réduction de la distorsion, Ajustement de l'échelle, Définition de la nouvelle taille d'image
    print('starting initUndistortRectifyMap')
    mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (640, 480), 5)  # The function computes the joint undistortion and rectification transformation and represents 
                                                                                            # the result in the form of maps for remap. The undistorted image looks like original, 
                                                                                            # as if it is captured with a camera using the camera matrix =newCameraMatrix and zero distortion.

    # debug_print("starting video_cap.read()")
    # has_frame, img = video_cap.read()
    # frame_w = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # frame_h = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # fps = int(video_cap.get(cv2.CAP_PROP_FPS))
    # print(f'Weidth: {frame_w}, height: {frame_h}, fps: {fps}')

    print("Press q or esc to exit")
    # Enter a while loop to read and display the video frames one at a time.
    while True:
        # Read one frame at a time using the video capture object.
        #debug_print("starting video_cap.read()")
        has_frame, img = video_cap.read()
        if not has_frame:
            print("No frame!")
            no_frame_count += 1
            time.sleep(0.01)
        else:
            frame_count += 1
            debug_print(frame_count)
            frame = img.copy()
            frame = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)  # Réduction de la distorsion, Ajustement de l'échelle 
            Frame = img_processing(frame)           # Run image processing on frame
            cv2.imshow(win_name, Frame)             # Display the current frame in the named window.

        if not LAPTOP_TEST:
            if LastHeartbeat < time.time():
                heartBeat()

        # Use the waitKey() function to monitor the keyboard for user input.
        # key = cv2.waitKey(0) will display the window indefinitely until any key is pressed.
        # key = cv2.waitKey(1) will display the window for 1 ms
        key = cv2.waitKey(1)

        # The return value of the waitKey() function indicates which key was pressed.
        # You can use this feature to check if the user selected the `q` key to quit the video stream.
        if (key == ord('Q')) or (key == ord('q')) or (key == 27) or (frame_count > 1000) or (no_frame_count > 20):
            print("Exit loop")
            break

    time.sleep(1)       # wait 3 seconds to look at the result
    if not LAPTOP_TEST:
        stop_streaming_server()
    video_cap.release()
    cv2.destroyWindow(win_name)
