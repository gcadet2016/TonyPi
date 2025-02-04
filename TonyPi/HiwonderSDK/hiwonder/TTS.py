#!/usr/bin/env python3
# coding=utf8
import time
import smbus  # Appelez le Raspberry Pi Ikku


# Hiwonder I2C ultrasonic usage routine
# The I2C baud rate needs to be set to 40000 before using
# Add the following line at the end of /boot/config.txt: dtparam=i2c1_baudrate=40000
# If already added, you can skip this step. Then restart the system

class TTS:
      
    address = 0x40
    bus = None

    def __init__(self, bus=1):
        self.bus = smbus.SMBus(bus)
    
    def WireReadTTSDataByte(self):
        try:
            val = self.bus.read_byte(self.address)
        except:
            return False
        return True
    
    def TTSModuleSpeak(self, sign, words):
        head = [0xFD,0x00,0x00,0x01,0x00]              # The text playback command
        words_list = words.encode("gb2312")            # Set the text encoding format to GB2312
        sign_data = sign.encode("gb2312")    
        length = len(sign_data) + len(words_list) + 2
        head[1] = length >> 8
        head[2] = length
        head.extend(list(sign_data))
        head.extend(list(words_list))       
        try:
            self.bus.write_i2c_block_data(self.address, 0, head) # Send data to the slave device
        except:
            print('Sensor not connected!')
        time.sleep(0.05)
        
if __name__ == '__main__':
    v = TTS()
    # [h0]set the pronunciation mode for words. 
    #   0 for automatic detection of pronunciation mode, 
    #   1 for letter-by-letter pronunciation mode, 
    #   2 for word pronunciation mode
    # [v10]set the volume, with a range of 0-10, where 10 is the maximum volume
    # for more methods, please refer to the manual
    v.TTSModuleSpeak("[h0][v10]","Bonjour")   
    # please note that the length of characters inside parentheses cannot exceed 32. If it exceeds, please split it into multiple parts
    time.sleep(1) # please allow for an appropriate delay to ensure speech completion
