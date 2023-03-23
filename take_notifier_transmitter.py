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

import protocols

class Radio():
    def __init__(self):
        self.spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        self.cs = digitalio.DigitalInOut(board.CE1)
        self.reset = digitalio.DigitalInOut(board.D25)
        self.freq = 915.0
        self.rfm9x = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.freq)


    def SendTakeSignal(self, device_uuid):
        msg = bytes("Take Signal", "utf-8")
        for i in range(10):
            self.rfm9x.send(msg)
            time.sleep(.1)
    
    def SendPairSignal(self, device_uuid):
        msg = bytes(device_uuid, " PAIR")
    
    def SendACK(self, device_uuid):
        msg = bytes(device_uuid, " ACK")
    
    def listen(self, device_uuid):
        msg = self.rfm9x.receive()
        if msg is not None:
            msg = msg.split()
            if (msg[0] == device_uuid) and (len(msg) > 1):
                if msg[1] == 'ACK':
                    # notify user
                    self.SendACK(device_uuid)
                    return 0
        
        return -1
                

    def SyncMode(self, device_uuid):
        isACK = -1

        while(isACK != 0):
            self.SendPairSignal(device_uuid)
            isACK = self.listen(device_uuid)
    
        return 0
            
        

def main():
    # attempt to get device's uuid
    device_uuid, code = protocols.get_UUID()
    if(code < 0):
        # generate a new uuid
        # notify switch to sync mode
        device_uuid, code = protocols.generate_UUID()
        if(code < 0):
            # notify of catastrophic error
            print("Catastrophic error has occured! Code: ", code) # TODO: convert to logging statement

    # go into sync mode:
    isACK = False
    radio = Radio()

    while()
