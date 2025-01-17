#!/usr/bin/python3
# coding=utf8
import sys
import os
import cv2
import math
import time
import threading
import numpy as np
import hiwonder.Camera as Camera
import hiwonder.Misc as Misc
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller
import hiwonder.ActionGroupControl as AGC
import hiwonder.yaml_handle as yaml_handle


'''
    程序功能：颜色识别(program function: color recognition)

    运行效果：将红色小球放置到摄像头前，机器人在识别到后将会“点头”；将蓝色或绿色小球放置
             到摄像头前，机器人识别到后将会“摇头”。(running effect: place the red ball in front of the camera. The robot will 'nod' once it recognizes it. Place the blue or green ball in front of the camera. The robot will 'shake its head' once it recognizes it)


    对应教程文档路径：  TonyPi智能视觉人形机器人\3.AI视觉玩法学习\第3课 颜色识别(corresponding tutorial file path: TonyPi Intelligent Vision Humanoid Robot\3.AI Vision Game Course\Lesson3 Color Recognition)
'''

# 调试模式标志量(debug mode flag variable)
debug = False

# 检查 Python 版本是否为 Python 3，若不是则打印提示信息并退出程序(check if the Python version is Python 3. If not, print a prompt message and exit the program)
if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

range_rgb = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}

# 找出面积最大的轮廓(find the contour with the maximal area)
# 参数为要比较的轮廓的列表(parameter is the list of contour to be compared)
def getAreaMaxContour(contours):
    contour_area_temp = 0
    contour_area_max = 0
    areaMaxContour = None

    for c in contours:  # 历遍所有轮廓(iterate through all contours)
        contour_area_temp = math.fabs(cv2.contourArea(c))  # 计算轮廓面积(calculate contour area)
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 50:  # 只有在面积大于50时，最大面积的轮廓才是有效的，以过滤干扰(only contours with an area greater than 50 are considered valid; the contour with the largest area is used to filter out interference)
                areaMaxContour = c

    return areaMaxContour, contour_area_max  # 返回最大的轮廓(return the contour with the maximal area)

board = rrc.Board()
ctl = Controller(board)


lab_data = None
servo_data = None

# 加载配置文件数据(load configuration file data)
def load_config():
    global lab_data, servo_data
    
    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)

# 初始化机器人舵机初始位置(initialize the servo initialization position of robot)
def initMove():
    ctl.set_pwm_servo_pulse(1, 1500, 500)
    ctl.set_pwm_servo_pulse(2, servo_data['servo2'], 500)
   
    
color_list = []
detect_color = 'None'
action_finish = True
draw_color = range_rgb["black"]
# 变量重置(variable reset)
def reset():
    global draw_color
    global color_list
    global detect_color
    global action_finish
    
    color_list = []
    detect_color = 'None'
    action_finish = True
    draw_color = range_rgb["black"]

# app初始化调用(app initialization calling)
def init():
    print("ColorDetect Init")
    load_config()
    initMove()

__isRunning = False
# app开始玩法调用(app start program calling)
def start():
    global __isRunning
    reset()
    __isRunning = True
    print("ColorDetect Start")

# app停止玩法调用(app stop program calling)
def stop():
    global __isRunning
    __isRunning = False
    print("ColorDetect Stop")

# app退出玩法调用(app exit program calling)
def exit():
    global __isRunning
    __isRunning = False
    AGC.runActionGroup('stand_slow')
    print("ColorDetect Exit")


def move():
    global draw_color
    global detect_color
    global action_finish

    while True:
        if debug:
            return     
        if __isRunning:
            if detect_color != 'None':
                action_finish = False

                if detect_color == 'red':
                    ctl.set_pwm_servo_pulse(1, 1800, 200)
                    time.sleep(0.2)
                    ctl.set_pwm_servo_pulse(1, 1200, 200)
                    time.sleep(0.2)
                    ctl.set_pwm_servo_pulse(1, 1800, 200)
                    time.sleep(0.2)
                    ctl.set_pwm_servo_pulse(1, 1200, 200)
                    time.sleep(0.2)
                    ctl.set_pwm_servo_pulse(1, 1500, 100)
                    time.sleep(0.1)

                    detect_color = 'None'
                    draw_color = range_rgb["black"]                    
                    time.sleep(1)

                elif detect_color == 'green' or detect_color == 'blue':
                    ctl.set_pwm_servo_pulse(2, 1800, 200)
                    time.sleep(0.2)
                    ctl.set_pwm_servo_pulse(2, 1200, 200)
                    time.sleep(0.2)
                    ctl.set_pwm_servo_pulse(2, 1800, 200)
                    time.sleep(0.2)
                    ctl.set_pwm_servo_pulse(2, 1200, 200)
                    time.sleep(0.2)
                    ctl.set_pwm_servo_pulse(2, 1500, 100)
                    time.sleep(0.1)
                    detect_color = 'None'
                    draw_color = range_rgb["black"]                    
                    time.sleep(1)
                else:
                    time.sleep(0.01)                
                action_finish = True                
                detect_color = 'None'
            else:
               time.sleep(0.01)
        else:
            time.sleep(0.01)

# 运行子线程(run sub-thread)
th = threading.Thread(target=move)
th.daemon = True
th.start()

size = (320, 240)


if __name__ == '__main__':
    from CameraCalibration.CalibrationConfig import *
    
    param_data = np.load(calibration_param_path + '.npz')
    
    mtx = param_data['mtx_array']
    dist = param_data['dist_array']
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (640, 480), 0, (640, 480))
    mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (640, 480), 5)
   
    debug = False
    if debug:
        print('Debug Mode')
        
    init()
    start()
    open_once = yaml_handle.get_yaml_data('/boot/camera_setting.yaml')['open_once']
    #if open_once:
    my_camera = cv2.VideoCapture('http://127.0.0.1:8080/?action=stream?dummy=param.mjpg')
    # else:
    #     my_camera = Camera.Camera()
    #     my_camera.camera_open()             
    #AGC.runActionGroup('stand')
    while True:
        ret, img = my_camera.read()
        if ret:
            frame = img.copy()
            frame = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)  # 鐣稿彉鐭
            cv2.imshow('Frame', frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    my_camera.camera_close()
    cv2.destroyAllWindows()
