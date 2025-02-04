import time
from hiwonder.ASR import ASR

'''
    Program function: voice recognition module routine)

    Running effect: Bring the microphone close to the speech recognition module, say the wake-up word first, which is entry 1 'kai shi', then say other entries. 
    The recognized entry numbers will be printed on the screen)

   Corresponding tutorial file path: TonyPi Intelligent Vision Humanoid Robot\4. Expanded Course\5. Raspberry Pi Expansion Board Course\Lesson 5 Raspberry Pi Voice Recognition)
'''

asr = ASR()

# Added entries and recognition modes can be saved even after power off. After the initial setup, you can change 1 to 0)
if 1:
    asr.eraseWords()                     # Clear the previously added entries)
    asr.setMode(2)                       # Set the recognition mode. The values 1 to 3 correspond to loop recognition mode, password mode, and button mode respectively. Here, set it to password mode)
    asr.addWords(1, 'kai shi')           # Add entries. In password mode, entry 1 is the wake-up word)
    asr.addWords(2, 'wang qian zou')
    asr.addWords(2, 'qian jin')
    asr.addWords(4, 'zhi zou')
    asr.addWords(2, 'wang hou tui')
    asr.addWords(3, 'wang zuo yi')
    asr.addWords(4, 'wang you yi')

while True:
    data = asr.getResult()               # 获取识别结果(get recognition result)
    
    if data:
        print("result:", data)
    elif data is None:
        print('Sensor not connected!')
        break
