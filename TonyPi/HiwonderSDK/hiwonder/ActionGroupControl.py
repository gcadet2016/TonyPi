# ActionGroupControl.py is a library for running action groups on the TonyPi robot.
# V1.1
# Tested 2025-01-17
#
#!/usr/bin/env python3
# encoding: utf-8
import os
import sys
import time
import threading
import sqlite3 as sql
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller

# PC edited action calling library

runningAction = False
stop_action = False
stop_action_group = False

board = rrc.Board()
ctl = Controller(board)

def stopAction():
    global stop_action
    
    stop_action = True

def stopActionGroup():
    global stop_action_group
    
    stop_action_group = True 

__end = False
__start = True
current_status = ''
def runActionGroup(actFileName, times=1, with_stand=False, lock_servos='', path="/home/pi/TonyPi/ActionGroups/"): 
    global __end
    global __start
    global current_status
    global stop_action_group
    
    temp = times
    while True:
        if temp != 0:
            times -= 1
        try:
            if (actFileName != 'go_forward' and actFileName != 'go_forward_fast' and actFileName != 'go_forward_slow' and actFileName != 'back' and actFileName != 'back_fast') or stop_action_group:
                if __end:
                    __end = False
                    if current_status == 'go':
                        runAction('go_forward_end', lock_servos, path=path)
                    else:
                        runAction('back_end', lock_servos, path=path)
                    
                if stop_action_group:
                    __end = False
                    __start = True
                    stop_action_group = False                        
                   
                    break
                __start = True
                if times < 0:
                    __end = False
                    __start = True
                    stop_action_group = False 
                    break
                runAction(actFileName, lock_servos, path=path)
            else:
                if times < 0:
                   
                    if with_stand:
                        if actFileName == 'go_forward' or actFileName == 'go_forward_fast' or actFileName == 'go_forward_slow':
                            runAction('go_forward_end', lock_servos, path=path)
                        else:
                            runAction('back_end', lock_servos, path=path)
                    break
                if __start:
                    __start = False
                    __end = True
                    
                    if actFileName == 'go_forward' or actFileName == 'go_forward_slow':                       
                        runAction('go_forward_start', lock_servos, path=path)
                        current_status = 'go'
                    elif actFileName == 'go_forward_fast':
                        runAction('go_forward_start_fast', lock_servos, path=path)
                        current_status = 'go'
                    elif actFileName == 'back':
                        runAction('back_start', lock_servos, path=path)
                        runAction('back', lock_servos, path=path)
                        current_status = 'back'                    
                    elif actFileName == 'back_fast':
                        runAction('back_start', lock_servos, path=path)
                        runAction('back_fast', lock_servos, path=path)
                        current_status = 'back'
                else:
                    runAction(actFileName, lock_servos, path=path)
        except BaseException as e:
            print(e)

def runAction(actFileName, lock_servos='', path="/home/pi/TonyPi/ActionGroups/"):
    '''
    run the action group, cannot send stop signal
    :param actFileName: action group name, string type
    :return:
    '''
    global runningAction
    global stop_action
    
    if actFileName is None:
        return

    actFileName = path + actFileName + ".d6a"

    if os.path.exists(actFileName) is True:
        if runningAction is False:
            runningAction = True
            ag = sql.connect(actFileName)
            cu = ag.cursor()
            cu.execute("select * from ActionGroup")
            while True:
                act = cu.fetchone()
                if stop_action is True:
                    stop_action = False
                    print('stop')                    
                    break
                if act is not None:
                    for i in range(0, len(act) - 2, 1):
                        if str(i + 1) in lock_servos:
                            ctl.set_bus_servo_pulse(i+1, lock_servos[str(i + 1)], act[1])
                            
                        else:
                            ctl.set_bus_servo_pulse(i+1, act[2 + i], act[1])
                    time.sleep(float(act[1])/1000.0)
                else:   # exit after running
                    break
            runningAction = False
            
            cu.close()
            ag.close()
    else:
        runningAction = False
        print("File not found:{}".format(actFileName, path))
