#!/usr/bin/python3
# coding=utf8
import sys
import os
import cv2
import time
import math
import threading
import numpy as np

import hiwonder.apriltag as apriltag
import hiwonder.Camera as Camera
import hiwonder.Misc as Misc
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller
import hiwonder.ActionGroupControl as AGC
import hiwonder.yaml_handle as yaml_handle

DEBUG = True
APP_VERSION = "Transport_v2.py v2.0"

def debugPrint(s):
    if DEBUG :
        print(s)

'''
    program function: intelligent transportation

    running effect: place the robot and the red, green, and blue sponge blocks randomly in the placement area of the map. 
                    After starting the smart handling gameplay, the robot will sequentially transport the sponge blocks to 
                    the corresponding AprilTag labels based on distance, until all three blocks are transported
                    

    Corresponding tutorial file path: TonyPi Intelligent Vision Humanoid Robot\4.Expanded Courses\1.Voice Interaction and Intelligent Transportation(voice module optional)\Lesson4 Intelligent Transportation)
'''

if __name__ == '__main__':
    from CameraCalibration.CalibrationConfig import *
    print(APP_VERSION)
    print(f'Debug : {DEBUG}')
else:
    from Functions.CameraCalibration.CalibrationConfig import *

# Check if the Python version is Python 3. If not, print a prompt message and exit the program
if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

# Load parameters
param_data = np.load(calibration_param_path + '.npz')

# Get parameters
mtx = param_data['mtx_array']
dist = param_data['dist_array']
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (640, 480), 0, (640, 480))
mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (640, 480), 5)

# The names of action groups used for transportation
go_forward = 'go_forward'
back = 'back_fast'
turn_left = 'turn_left_small_step'
turn_right = 'turn_right_small_step'
left_move = 'left_move'
right_move = 'right_move'
left_move_large = 'left_move_30'
right_move_large = 'right_move_30'

range_rgb = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}

# The tag numbers corresponding to colors
color_tag = {'red': 1,
             'green': 2,
             'blue': 3
             }

lab_data = None
servo_data = None
# Load configuration file data
def load_config():
    global lab_data, servo_data
    
    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)

load_config()

board = rrc.Board()
ctl = Controller(board)

# Initialize the servo initialization position of robot
def initMove():
    ctl.set_pwm_servo_pulse(1, servo_data['servo1'], 500)
    ctl.set_pwm_servo_pulse(2, servo_data['servo2'], 500)

# Initialize the step size for servo movement in the horizontal and vertical directions
d_x = 15
d_y = 15

step = 1
debugPrint("step 1")

# Initialize the timestamp for starting the timer
time_start = 0

# Set the servo position
x_dis = servo_data['servo2']
y_dis = servo_data['servo1']

# Initialize the previous state of the robot
last_status = ''

# Initialize the flag variable for starting the timer
start_count = True

# Initialize the center coordinates and diagonal angle of the sponge block
object_center_x, object_center_y, object_angle = -2, -2, 0

# Turning direction
turn = 'None'

# The x-coordinate of the image center
CENTER_X = 350

# True indicates the transportation stage, False indicates the placement stage
find_box = True

# The number of times the forward action group is executed
go_step = 3

# Servo lock, used to fix the position of the hand servo during transportation
lock_servos = ''

stop_detect = False
object_color = 'red'
haved_find_tag = False
head_turn = 'left_right'
color_list = ['red', 'green', 'blue']
color_center_x, color_center_y = -1, -1

# Variable reset
def reset():
    global color_list
    global time_start
    global d_x, d_y
    global last_status
    global start_count
    global step, head_turn
    global x_dis, y_dis
    global object_center_x, object_center_y, object_angle
    global turn
    global find_box
    global go_step
    global lock_servos
    global stop_detect
    global object_color
    global haved_find_tag
    global color_center_x, color_center_y

    d_x = 15
    d_y = 15
    step = 1
    time_start = 0
    x_dis = servo_data['servo2']
    y_dis = servo_data['servo1']
    last_status = ''
    start_count = True
    head_turn = 'left_right'
    object_center_x, object_center_y, object_angle = -2, -2, 0
 
    turn = 'None'
    find_box = True
    go_step = 3
    lock_servos = ''
    stop_detect = False
    object_color = 'red'
    haved_find_tag = False
    color_list = ['red', 'green', 'blue']
    color_center_x, color_center_y = -1, -1

# app initialization calling
def init():
    print("Transport Init")
    load_config()
    initMove()

__isRunning = False
# app start program calling
def start():
    global __isRunning
    reset()
    __isRunning = True
    print("Transport Start")

# app stop program calling
def stop():
    global __isRunning
    __isRunning = False
    print("Transport Stop")

# app exit program calling
def exit():
    global __isRunning
    __isRunning = False
    AGC.runActionGroup('stand_slow')
    print("Transport Exit")

# find out the contour with the maximal area
# parameter is the list of contour to be compared
def getAreaMaxContour(contours):
    contour_area_temp = 0
    contour_area_max = 0
    areaMaxContour = None

    for c in contours:  # iterate through all contours
        contour_area_temp = math.fabs(cv2.contourArea(c))  # calculate contour area
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 10:  # only contours with an area greater than 300 are considered valid; the contour with the largest area is used to filter out interference
                areaMaxContour = c

    return areaMaxContour, contour_area_max  # return the contour with the maximal area


# red-green-blue color recognition
size = (320, 240)
def colorDetect(img):
    img_h, img_w = img.shape[:2]
    
    frame_resize = cv2.resize(img, size, interpolation=cv2.INTER_NEAREST)
    frame_gb = cv2.GaussianBlur(frame_resize, (3, 3), 3)   
    frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # convert the image to LAB space
    
    center_max_distance = pow(img_w/2, 2) + pow(img_h, 2)
    color, center_x, center_y, angle = 'None', -1, -1, 0
    for i in lab_data:
        if i in color_list:
            frame_mask = cv2.inRange(frame_lab,
                                     (lab_data[i]['min'][0],
                                      lab_data[i]['min'][1],
                                      lab_data[i]['min'][2]),
                                     (lab_data[i]['max'][0],
                                      lab_data[i]['max'][1],
                                      lab_data[i]['max'][2]))  # perform bitwise operation to original image and mask
            eroded = cv2.erode(frame_mask, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))  # corrosion
            dilated = cv2.dilate(eroded, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))) # dilation
            contours = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # find out contours
            areaMaxContour, area_max = getAreaMaxContour(contours)  # find out the contour with the maximal area
            
            if area_max > 500:  # the maximal area is found
                rect = cv2.minAreaRect(areaMaxContour)# the minimum bounding rectangle
                angle_ = rect[2]
        
                box = np.int0(cv2.boxPoints(rect))# four vertices of the minimum bounding rectangle
                for j in range(4):
                    box[j, 0] = int(Misc.map(box[j, 0], 0, size[0], 0, img_w))
                    box[j, 1] = int(Misc.map(box[j, 1], 0, size[1], 0, img_h))

                cv2.drawContours(img, [box], -1, (0,255,255), 2)# draw a rectangle formed by four points
            
                # obtain the diagonal points of a rectangle
                ptime_start_x, ptime_start_y = box[0, 0], box[0, 1]
                pt3_x, pt3_y = box[2, 0], box[2, 1]            
                center_x_, center_y_ = int((ptime_start_x + pt3_x) / 2), int((ptime_start_y + pt3_y) / 2)# center point
                cv2.circle(img, (center_x_, center_y_), 5, (0, 255, 255), -1)# draw center point
                
                distance = pow(center_x_ - img_w/2, 2) + pow(center_y_ - img_h, 2)
                if distance < center_max_distance:  #  find the nearest object to transport
                    center_max_distance = distance
                    color = i
                    center_x, center_y, angle = center_x_, center_y_, angle_
                    
    return color, center_x, center_y, angle

#  detect apriltag
detector = apriltag.Detector(searchpath=apriltag._get_demo_searchpath())
def apriltagDetect(img):   
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    detections = detector.detect(gray, return_image=False)
    tag_1 = [-1, -1, 0]
    tag_2 = [-1, -1, 0]
    tag_3 = [-1, -1, 0]

    if len(detections) != 0:
        for detection in detections:                       
            corners = np.rint(detection.corners)  # get four corner points
            cv2.drawContours(img, [np.array(corners, int)], -1, (0, 255, 255), 2)

            tag_family = str(detection.tag_family, encoding='utf-8')  # get tag_family
            tag_id = str(detection.tag_id)  # get tag_id

            object_center_x, object_center_y = int(detection.center[0]), int(detection.center[1])  # center point
            cv2.circle(frame, (object_center_x, object_center_y), 5, (0, 255, 255), -1)
            
            object_angle = int(math.degrees(math.atan2(corners[0][1] - corners[1][1], corners[0][0] - corners[1][0])))  # calculate rotation angle
            
            if tag_family == 'tag36h11':
                if tag_id == '1':
                    tag_1 = [object_center_x, object_center_y, object_angle]
                elif tag_id == '2':
                    tag_2 = [object_center_x, object_center_y, object_angle]
                elif tag_id == '3':
                    tag_3 = [object_center_x, object_center_y, object_angle]
        
    return tag_1, tag_2, tag_3

# Determine the position of the target apriltag using Other apriltags
# apriltag placement: red(tag36h_11_1), green(tag36h11_2), blue(tag36h11_3)
def getTurn(tag_id, tag_data):
    tag_1 = tag_data[0]
    tag_2 = tag_data[1]
    tag_3 = tag_data[2]

    if tag_id == 1:  # target apriltag is 1)
        if tag_2[0] == -1:  # apriltag 2 is not detected)
            if tag_3[0] != -1:  # detected apriltag 3, therefore apriltag 1 is to the left of apriltag 3, so turn left)
                return 'left'
        else:  # detected apriltag 2, therefore apriltag 1 is to the left of apriltag 2, so turn left)
            return 'left'
    elif tag_id == 2:
        if tag_1[0] == -1:
            if tag_3[0] != -1:
                return 'left'
        else:
            return 'right'
    elif tag_id == 3:
        if tag_1[0] == -1:
            if tag_2[0] != -1:
                return 'right'
        else:
            return 'right'

    return 'None'

LOCK_SERVOS = {'6': 650, '7': 850, '8': 0, '14': 350, '15': 150, '16': 1000}
# perform action group
def move(): 
    global d_x
    global d_y
    global step
    global turn
    global x_dis
    global y_dis
    global go_step
    global lock_servos
    global start_count
    global find_box
    global head_turn
    global time_start
    global color_list
    global stop_detect
    global haved_find_tag    
    
    while True:
        if __isRunning:
            if object_center_x == -3:  # -3 indicates the placement phase, and the target apriltag was not found, but other AprilTags were detected
                # Determine the turning direction based on the relative positions of other apriltags
                if turn == 'left':
                    AGC.runActionGroup(turn_left, lock_servos=lock_servos)
                elif turn == 'right':
                    AGC.runActionGroup(turn_right, lock_servos=lock_servos)
            elif haved_find_tag and object_center_x == -1:  # if an apriltag is found during the turning process, but it is not in view when the head returns to center position
                # determine the position of the apriltag based on the head orientation
                if x_dis > servo_data['servo2']:                    
                    AGC.runActionGroup(turn_left, lock_servos=lock_servos)
                elif x_dis < servo_data['servo2']:
                    AGC.runActionGroup(turn_right, lock_servos=lock_servos)
                else:
                    debugPrint(f'haved_find_tag:{haved_find_tag}')
                    haved_find_tag = False
            elif object_center_x >= 0:  # if target is found
                if not find_box:  # if it is placement stage
                    if color_center_y > 350:  # during the transportation process, when too close to other objects, it's necessary to navigate around them
                        if (color_center_x - CENTER_X) > 80:
                            AGC.runActionGroup(go_forward, lock_servos=lock_servos)
                        elif (color_center_x > CENTER_X and object_center_x >= CENTER_X) or (color_center_x <= CENTER_X and object_center_x >= CENTER_X):
                            AGC.runActionGroup(right_move_large, lock_servos=lock_servos)
                            #time.sleep(0.2)
                        elif (color_center_x > CENTER_X and object_center_x < CENTER_X) or (color_center_x <= CENTER_X and object_center_x < CENTER_X):
                            AGC.runActionGroup(left_move_large, lock_servos=lock_servos)
                            #time.sleep(0.2)

                # if an object is found during the head turning phase, return the head to the center position
                if x_dis != servo_data['servo2'] and not haved_find_tag:
                    # reset the relevant variables for head scanning
                    head_turn == 'left_right'
                    start_count = True
                    d_x, d_y = 15, 15
                    haved_find_tag = True
                    debugPrint(f'haved_find_tag:{haved_find_tag}')
                    
                    # head returns to center
                    ctl.set_pwm_servo_pulse(1, servo_data['servo1'], 500)
                    ctl.set_pwm_servo_pulse(2, servo_data['servo2'], 500)
                    time.sleep(0.6)
                elif step == 1:  # adjust left or right to maintain in the center
                    x_dis = servo_data['servo2']
                    y_dis = servo_data['servo1']                   
                    turn = ''
                    haved_find_tag = False
                    debugPrint(f'haved_find_tag:{haved_find_tag}')
                    debugPrint(f'{object_center_x - CENTER_X},{object_center_y}')

                    if (object_center_x - CENTER_X) > 170 and object_center_y > 330:
                        AGC.runActionGroup(back, lock_servos=lock_servos)   
                    elif object_center_x - CENTER_X > 80:  # not in the center, turn the robot one step according to the direction)
                        AGC.runActionGroup(turn_right, lock_servos=lock_servos)
                    elif object_center_x - CENTER_X < -80:
                        AGC.runActionGroup(turn_left, lock_servos=lock_servos)                        
                    elif 0 < object_center_y <= 250:
                        AGC.runActionGroup(go_forward, lock_servos=lock_servos)
                    else:
                        step = 2
                        debugPrint("step 2")
                elif step == 2:  # approach the object
                    debugPrint(f'{object_center_x - CENTER_X},{object_center_y}')
                    if 330 < object_center_y:
                        AGC.runActionGroup(back, lock_servos=lock_servos)
                    if find_box:
                        if object_center_x - CENTER_X > 150:  
                            AGC.runActionGroup(right_move_large, lock_servos=lock_servos)
                        elif object_center_x - CENTER_X < -150:
                            AGC.runActionGroup(left_move_large, lock_servos=lock_servos)                        
                        elif -10 > object_angle > -45:# not in the center, turn the robot one step according to the direction
                            AGC.runActionGroup(turn_left, lock_servos=lock_servos)
                        elif -80 < object_angle <= -45:
                            AGC.runActionGroup(turn_right, lock_servos=lock_servos)
                        elif object_center_x - CENTER_X > 40:  
                            AGC.runActionGroup(right_move_large, lock_servos=lock_servos)
                        elif object_center_x - CENTER_X < -40:
                            AGC.runActionGroup(left_move_large, lock_servos=lock_servos)
                        else:
                            step = 3
                            debugPrint("step 3")
                    else:                        
                        if object_center_x - CENTER_X > 150:  
                            AGC.runActionGroup(right_move_large, lock_servos=lock_servos)
                        elif object_center_x - CENTER_X < -150:
                            AGC.runActionGroup(left_move_large, lock_servos=lock_servos)                        
                        elif object_angle < -5:# not in the center, turn the robot one step according to the direction
                            AGC.runActionGroup(turn_left, lock_servos=lock_servos)
                        elif 5 < object_angle:
                            AGC.runActionGroup(turn_right, lock_servos=lock_servos)
                        elif object_center_x - CENTER_X > 40:  
                            AGC.runActionGroup(right_move_large, lock_servos=lock_servos)
                        elif object_center_x - CENTER_X < -40:
                            AGC.runActionGroup(left_move_large, lock_servos=lock_servos)
                        else:
                            step = 3
                            debugPrint("step 3")
                elif step == 3:
                    debugPrint(f'{object_center_x - CENTER_X},{object_center_y}')
                    if 340 < object_center_y:
                        AGC.runActionGroup(back, lock_servos=lock_servos)
                    elif 0 < object_center_y <= 250:
                        AGC.runActionGroup(go_forward, lock_servos=lock_servos)
                    elif object_center_x - CENTER_X >= 40:  # not in the center, move the robot left or right one step according to the position
                        AGC.runActionGroup(right_move_large, lock_servos=lock_servos)
                    elif object_center_x - CENTER_X <= -40:
                        AGC.runActionGroup(left_move_large, lock_servos=lock_servos) 
                    elif 20 <= object_center_x - CENTER_X < 40:  
                        AGC.runActionGroup(right_move, lock_servos=lock_servos)
                    elif -40 < object_center_x - CENTER_X < -20:                      
                        AGC.runActionGroup(left_move, lock_servos=lock_servos)
                    else:
                        step = 4 
                        debugPrint("step 4")
                elif step == 4:  # Approach the object
                    debugPrint(f'{object_center_x - CENTER_X},{object_center_y}')
                    if 280 < object_center_y <= 340:
                        AGC.runActionGroup('go_forward_one_step', lock_servos=lock_servos)
                        time.sleep(0.2)
                    elif 0 <= object_center_y <= 280:
                        AGC.runActionGroup(go_forward, lock_servos=lock_servos)
                    else:
                        if object_center_y >= 370:
                            go_step = 2
                        else:
                            go_step = 3
                        if abs(object_center_x - CENTER_X) <= 40:
                            stop_detect = True
                            step = 5
                            debugPrint("step 5")
                        else:
                            step = 3
                            debugPrint("step 3")
                elif step == 5:  # pick up or put down the object
                    debugPrint(f'find_box:{find_box}')
                    if find_box:
                        AGC.runActionGroup('go_forward_one_step', times=2)
                        AGC.runActionGroup('stand', lock_servos=lock_servos)
                        AGC.runActionGroup('move_up')
                        lock_servos = LOCK_SERVOS
                        step = 6  
                        debugPrint("step 6")  
                    else:
                        AGC.runActionGroup('go_forward_one_step', times=go_step, lock_servos=lock_servos)
                        AGC.runActionGroup('stand', lock_servos=lock_servos)
                        AGC.runActionGroup('put_down')
                        AGC.runActionGroup(back, times=5, with_stand=True)
                        color_list.remove(object_color)
                        if color_list == []:
                            color_list = ['red', 'green', 'blue']
                        lock_servos = ''
                        step = 6
                        debugPrint("step 6")
            elif object_center_x == -1:  # when the target cannot be found, turn the head or rotate the body to search
                #debugPrint(f'{object_center_x},{object_center_y}')
                if start_count:
                    start_count = False
                    time_start = time.time()
                else:
                    if time.time() - time_start > 0.5:
                        if 0 < servo_data['servo2'] - x_dis <= abs(d_x) and d_y > 0:
                            x_dis = servo_data['servo2']
                            y_dis = servo_data['servo1']
                            ctl.set_pwm_servo_pulse(1, y_dis, 20)
                            ctl.set_pwm_servo_pulse(2, x_dis, 20)
                            
                            AGC.runActionGroup(turn_right, times=3, lock_servos=lock_servos)
                        elif head_turn == 'left_right':
                            x_dis += d_x            
                            if x_dis > servo_data['servo2'] + 400 or x_dis < servo_data['servo2'] - 200:
                                if head_turn == 'left_right':
                                    head_turn = 'up_down'
                                d_x = -d_x
                        elif head_turn == 'up_down':
                            y_dis += d_y
                            if y_dis > servo_data['servo1'] + 300 or y_dis < servo_data['servo1']:
                                if head_turn == 'up_down':
                                    head_turn = 'left_right'
                                d_y = -d_y
                        ctl.set_pwm_servo_pulse(1, y_dis, 20)
                        ctl.set_pwm_servo_pulse(2, x_dis, 20)
                        
                        time.sleep(0.02)
            else:
                time.sleep(0.01)
        else:
            time.sleep(0.01)

# start the action thread
th = threading.Thread(target=move)
th.daemon = True
th.start()

def run(img):
    global step 
    global turn
    global stop_detect, find_box
    global color, color_center_x, color_center_y, color_angle
    global object_color, object_center_x, object_center_y, object_angle

    if not __isRunning or stop_detect:
        if step == 5:
            object_center_x = 0
        elif step == 6:
            find_box = not find_box
            object_center_x = -2
            step = 1
            debugPrint("step 1")
            stop_detect = False
       

        return img
    
    color, color_center_x, color_center_y, color_angle = colorDetect(img)  # color detection, return color, center coordinates, angle
    
    # if it is the transportation stage
    if find_box:
        object_color, object_center_x, object_center_y, object_angle = color, color_center_x, color_center_y, color_angle
    else:
        tag_data = apriltagDetect(img) # apriltag detection

        if tag_data[color_tag[object_color] - 1][0] != -1:  # if the target apriltag is detected
            object_center_x, object_center_y, object_angle = tag_data[color_tag[object_color] - 1]
        else:  # if the target AprilTag is not detected, then determine the relative position using other apriltags
            turn = getTurn(color_tag[object_color], tag_data)
            if turn == 'None':
                object_center_x, object_center_y, object_angle = -1, -1, 0
            else:  # if no AprilTag is detected at all
                object_center_x, object_center_y, object_angle = -3, -1, 0
    
    return img

if __name__ == '__main__':
    init()
    start()
    
    open_once = yaml_handle.get_yaml_data('/boot/camera_setting.yaml')['open_once']
    if open_once:
        my_camera = cv2.VideoCapture('http://127.0.0.1:8080/?action=stream?dummy=param.mjpg')
    else:
        my_camera = Camera.Camera()
        my_camera.camera_open()         
    AGC.runActionGroup('stand_slow')
    while True:
        ret, img = my_camera.read()
        if ret:
            frame = img.copy()
            Frame = run(frame)
            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    my_camera.camera_close()
    cv2.destroyAllWindows()
