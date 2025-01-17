# ActionGroupControlDemo.py
# Version 1.0
#
# Run locally on TonyPi
#
import time
import threading
import hiwonder.ActionGroupControl as AGC

'''
    Invoke un action group

    running effect: first, execute the 'stand' action to stand at attention. 
    Then, perform the 'go_forward' action group twice to move forward. 
    Finally, execute the 'go_forward' action group in a loop for 3 seconds before stopping
    
    corresponding tutorial file path: TonyPi Intelligent Vision Humanoid Robot\4. Expanded Courses\3. TonyPi PC and Action Editing Learning\Lesson5 Call the Action Group via Command Line)
'''


# Default directory : the action groups need to be saved in the directory /home/pi/TonyPi/ActionGroup/
# Ce path est hardcodé par défaut dans /home/pi/TonyPi/HiwonderSDK/build/lib/hiwonder/ActionGroupControl.py

AGC.runActionGroup('stand')                                                        # The parameter is the name of the action group, without the file extension (.d6a), passed as a string)
AGC.runActionGroup('go_forward', times=2, with_stand=True)                         # The second parameter is the number of times the action should run, defaulting to 1. When set to 0, it indicates continuous looping. 
                                                                                   # The third parameter indicates whether to end in the 'stand' posture after the final action
# Il y a 2 autres paramètres notamment path qui permet de localiser le dossier des fichiers .db6  
time.sleep(3)

# The action function runs in a blocking manner. 
# If you want to run it in a loop for a period and then stop, you can use a thread to start it
# arguments: 
#   action name = 'go_forward'
#   repeat = 0      (infinite repeat until AGC.stopActionGroup())
#   with_stand = True
#   lock_servos=''  (default value)
#   path="/home/pi/TonyPi/ActionGroups/"  (default value)
#threading.Thread(target=AGC.runActionGroup, args=('go_forward', 0, True)).start()  
threading.Thread(target=AGC.runActionGroup, args=('stand', 0, True)).start()
time.sleep(3)
AGC.stopActionGroup()                                                              # move forward for 3 seconds and then stop
