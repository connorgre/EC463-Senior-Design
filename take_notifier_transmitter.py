# main code for the transmitter of the Take Notifer
import argparse
import os
import time
import struct
import wave
from datetime import datetime
from threading import Thread
import board
import digitalio
import pvporcupine
from pvrecorder import PvRecorder


import board
import busio
import digitalio
import adafruit_rfm9x
import time
from random import seed, randint
from 

import protocols

class Radio():
    def __init__(self, device_uuid):
        self.spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        self.cs = digitalio.DigitalInOut(board.CE1)
        self.reset = digitalio.DigitalInOut(board.D25)
        self.freq = 915.0
        self.rfm9x = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.freq)
        self.uuid = device_uuid


    def SendTakeSignal(self):
        msg = bytes(self.uuid, " Take Signal", "utf-8")
        for i in range(10):
            self.rfm9x.send(msg)
            # sleep for random fraction of seconds
            time.sleep(randint(1, 5) / 10) 
    
    # SendPairSignal and SendACK function with the principles of reliable data transfer
    def SendPairSignal(self):
        msg = bytes(self.uuid, " PAIR", "utf-8")

    
    def SendACK(self):
        msg = bytes(self.uuid, " ACK", "utf-8")
    
    def listen(self):
        msg = self.rfm9x.receive()
        if msg is not None:
            msg = msg.split()
            if (msg[0] == self.uuid) and (len(msg) > 1):
                if msg[1] == 'ACK':
                    # notify user
                    self.SendACK()
                    return 0
        
        return -1
                

    def SyncMode(self):
        isACK = -1

        while(isACK != 0):
            self.SendPairSignal()
            isACK = self.listen()
            self.SendACK()
        

    
        return 0
    
    def RunMode(self):

            
        

def main():
    # generate a new uuid
    device_uuid, code = protocols.generate_UUID()
    if(code < 0):
        # notify of catastrophic error
        print("Catastrophic error has occured! Code: ", code) # TODO: convert to logging statement

    # go into sync mode:
    isACK = False
    radio = Radio(device_uuid=device_uuid)

    radio.SyncMode()

    while()
