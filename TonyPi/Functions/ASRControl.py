#!/usr/bin/python3
# coding=utf8
import sys
import os
import time

import hiwonder.TTS as TTS
import hiwonder.ASR as ASR
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller
import hiwonder.ActionGroupControl as AGC
import hiwonder.yaml_handle as yaml_handle

'''
    Program function: voice control TonyPi

    running effect: Approach the microphone near the voice recognition module, and say the wake-up word 'start.' 
                    When the STA indicator light on the module turns solid blue, say other commands such as 'qianjin (forward)' or 'xianghoutui (move backward).' 
                    When recognized, the STA indicator light on the voice recognition module will turn off, and the voice playback module will play the sound 'received' as feedback. 
                    Then the robot will execute the corresponding action once
                    

    Corresponding tutorial file path: TonyPi Intelligent Vision Humanoid Robot\4.Expanded Courses\1.Voice Interaction and Intelligent Transportation(voice module optional)\Lesson2 Voice Control TonyPi)
'''

# Add the absolute path of the parent directory of the directory where the current script is located
last_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(last_dir_path)
from ActionGroupDict import action_group_dict

# Initialize the robot's low-level drivers
board = rrc.Board()
ctl = Controller(board)

# Get servo configuration data
servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)
try:
    asr = ASR.ASR()
    tts = TTS.TTS()

    asr.eraseWords()
    asr.setMode(2)
    asr.addWords(1, 'kai shi')
    asr.addWords(2, 'wang qian zou')
    asr.addWords(2, 'qian jin')
    asr.addWords(2, 'zhi zou')
    asr.addWords(3, 'wang hou tui')
    asr.addWords(4, 'xiang zuo yi')
    asr.addWords(5, 'xiang you yi')

    data = asr.getResult()
    ctl.set_pwm_servo_pulse(1, 1500, 500)
    ctl.set_pwm_servo_pulse(2, servo_data['servo2'], 500)
    AGC.runActionGroup('stand')
    action_finish = True
    tts.TTSModuleSpeak('[h0][v10][m3]', 'Prêt')
    print(''' In password mode, activation requires speaking the passphrase before each command
command: kai shi
command2:wang qian zou
command2: qian jin
command2: zhi zou
command3: wang hou tui
command4: xiang zuo yi
command5:xiang you yi''')
    time.sleep(2)
except:
    print('Une erreur s’est produite lors de l’initialisation du capteur')

while True:
    data = asr.getResult()
    if data:
        print('result:', data)
        tts.TTSModuleSpeak('', 'Bien reçu')
        time.sleep(1)
        AGC.runActionGroup(action_group_dict[str(data - 1)], 2 ,True)
    time.sleep(0.01)
