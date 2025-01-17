# ActionGroup_d6a.py
# Version 1.0
# Execute a custom .d6a file saved in /home/pi/TonyPi/Example/myActionGroup/
#
# Run locally on TonyPi
#

import threading
import hiwonder.ActionGroupControl as AGC
import time

def run_action(num):
    threading.Thread(target=AGC.runAction, args=(num, )).start() 

def run_my_action(num, path):
    threading.Thread(target=AGC.runAction, args=(num,'',path)).start()

def run_my_action_group(num, path, repeat=1):
    threading.Thread(target=AGC.runActionGroup, args=(num,repeat,True,'',path)).start()

# execute: /home/pi/TonyPi/ActionGroups/left_move_30.d6a
#run_action_group("left_move_30")
time.sleep(2)
AGC.runActionGroup('stand')
time.sleep(2)
run_my_action_group("test", "/home/pi/TonyPi/Example/myActionGroup/",2)