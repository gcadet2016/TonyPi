import time
from hiwonder.ASR import ASR

'''
    程序功能：语音识别模块例程(program function: voice recognition module routine)

    运行效果：靠近语音识别模块的麦克风，每次先说唤醒词，也即1号词条“kai shi”，再说其他词条，屏幕上会打印出识别到的词条编号(running effect: Bring the microphone close to the speech recognition module, say the wake-up word first, which is entry 1 'kai shi', then say other entries. 
    The recognized entry numbers will be printed on the screen)

    对应教程文档路径：  TonyPi智能视觉人形机器人\4.拓展课程学习\5.树莓派扩展板课程\第5课 树莓派语音识别(corresponding tutorial file path: TonyPi Intelligent Vision Humanoid Robot\4. Expanded Course\5. Raspberry Pi Expansion Board Course\Lesson 5 Raspberry Pi Voice Recognition)
'''

asr = ASR()

#添加的词条和识别模式是可以掉电保存的，第一次设置完成后，可以将1改为0(added entries and recognition modes can be saved even after power off. After the initial setup, you can change 1 to 0)
if 1:
    asr.eraseWords()                     # 清除之前添加的词条(clear the previously added entries)
    asr.setMode(2)                       # 设置识别模式，值范围1~3分别对应循环识别模式、口令模式、按键模式，这里设置为口令模式(set the recognition mode. The values 1 to 3 correspond to loop recognition mode, password mode, and button mode respectively. Here, set it to password mode)
    asr.addWords(1, 'kai shi')           # 添加词条，口令模式下1号词条为唤醒词(add entries. In password mode, entry 1 is the wake-up word)
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
