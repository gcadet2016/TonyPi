import time
from hiwonder.TTS import TTS

'''
    Program function: voice synthesis module routine

    Running effect: after the program starts, the speech recognition module will play the sound of 'hello' once

    corresponding tutorial file path:TonyPi Intelligent Vision Humanoid Robot\4. Expanded Courses\5. Raspberry Pi Expansion Board\Lesson 6 Raspberry Pi Voice Synthesis)
'''

tts = TTS()
time.sleep(1)
# [h0]set the pronunciation mode for words: 
#   0 for automatic pronunciation mode determination, 
#   1 for letter-by-letter pronunciation mode, 
#   2 for word-by-word pronunciation mode
# [v10]set the volume. The volume range is from 0 to 10, where 10 is the maximum volume

# Note that the character length inside the parentheses cannot exceed 32. If it exceeds, please split it into multiple parts
tts.TTSModuleSpeak("[h0][v10]","你好")   

time.sleep(1) # Ensure to introduce appropriate delays to allow for speech completion
