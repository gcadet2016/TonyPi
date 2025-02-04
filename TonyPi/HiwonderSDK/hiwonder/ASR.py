#!/usr/bin/env python3
# coding=utf8

'''
 * Only able to recognize Chinese characters, convert the to-be-recognized Chinese characters into pinyin letters, with a space between each character, such as "huan er ke ji"-->
 * up to 50 entries can be added, with each entry containing a maximum of 79 characters, and each entry consisting of no more than 10 Chinese characters)
 * Each entry corresponds to an identification number (arbitrarily set from 1 to 255). Different audio entries can correspond to the same identification number)
 * For example, both "幻尔科技" and "幻尔" can have the same identification number assigned
 * Module's STA status light: When it's on, it indicates that the speech recognition is in progress; when it's off, it means no speech recognition is taking place. When speech is recognized, the status light may dim or flash briefly, and it will return to its current status indication after the recognition process is completed)
'''

import smbus
import time
import numpy

# Hiwonder voice recognition module routine

class ASR:

    address = 0x79
    bus = None
    
    ASR_RESULT_ADDR = 100
    # Recognition result storage location, by continuously reading the value at this address to determine whether 
    # speech recognition has been achieved, with different values corresponding to different speech

    ASR_WORDS_ERASE_ADDR = 101
    # Erase all entries

    ASR_MODE_ADDR = 102
    #   Recognition mode setting, the value range is 1-3
    #1：1: Loop recognition mode. The status light is always on (default mode)
    #2：2: Password mode, using the first entry as the password. The status light is always off, and when the password is recognized, it remains on, waiting for a new speech recognition. After reading the recognition result, it goes off)
    #3：3: Button mode, recognition starts when the button is pressed, and stops when it's released. Supports power-off preservation. The status light lights up when the button is pressed and goes off when it's released)

    ASR_ADD_WORDS_ADDR = 160
    # The address for adding entries supports power-off preservation

    def __init__(self, bus=1):
        self.bus = smbus.SMBus(bus)
        
    def readByte(self):
        try:
            result = self.bus.read_byte(self.address)
        except:
            return None
        return result

    def writeByte(self, val):
        try:
            value = self.bus.write_byte(self.address, val)
        except:
            return False
        if value != 0:
            return False
        return True
    
    def writeData(self, reg, val):
        try:
            self.bus.write_byte(self.address,  reg)
            self.bus.write_byte(self.address,  val)
        except:
            pass

    def getResult(self):
        if ASR.writeByte(self, self.ASR_RESULT_ADDR):
            return -1        
        try:
            value = self.bus.read_byte(self.address)
        except:
            return None
        return value

    '''
    * Add entry function,
    * idNum：when the speech corresponding to the recognition number is detected, ranging from 1 to 255, it will be stored 
    *       at the 'asr_result_address' location, awaiting retrieval by the host. Once read, it will be cleared to 0
    * words：recognition of Chinese character entries in pinyin, with spaces between each Chinese character
    * 
    * Execute this function, where entries are automatically queued for addition  
    '''
    def addWords(self, idNum, words):
        buf = [idNum]       
        for i in range(0, len(words)):
            buf.append(eval(hex(ord(words[i]))))
        try:
            self.bus.write_i2c_block_data(self.address, self.ASR_ADD_WORDS_ADDR, buf)
        except:
            pass
        time.sleep(0.1)
        
    def eraseWords(self):
        try:
            result = self.bus.write_byte_data(self.address, self.ASR_WORDS_ERASE_ADDR, 0)
        except:
            return False
        time.sleep(0.1)
        if result != 0:
           return False
        return True
    
    def setMode(self, mode): 
        try:
            result = self.bus.write_byte_data(self.address, self.ASR_MODE_ADDR, mode)
        except:
            return False
        time.sleep(0.1)
        if result != 0:
           return False
        return True
        
if __name__ == "__main__":
    asr = ASR()

    # After the first setup, the added entries and recognition modes can be preserved even after power-off. 
    # Once set up, you can change 1 to 0
    if 1:
        asr.eraseWords()
        asr.setMode(2)
        asr.addWords(1, 'kai shi')
        asr.addWords(2, 'wang qian zou')
        asr.addWords(2, 'qian jin')
        asr.addWords(4, 'zhi zou')
        asr.addWords(2, 'wang hou tui')
        asr.addWords(3, 'wang zuo yi')
        asr.addWords(4, 'wang you yi')
    while 1:
        data = asr.getResult()
        if data:
            print("result:", data)
        elif data is None:
            print('Sensor not connected!')
            break
