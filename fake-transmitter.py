# Script to run on a second transmitter to interfere with the real device pair
import board
import busio
import digitalio
import adafruit_rfm9x

from time import sleep
from uuid import uuid4
from random import randint

class Radio():
    def __init__(self, device_uuid):
        self.spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        self.cs = digitalio.DigitalInOut(board.CE1)
        self.reset = digitalio.DigitalInOut(board.D25)
        self.freq = 915.0
        self.rfm9x = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.freq)
        self.uuid = device_uuid

        self.buzzerPin = digitalio.DigitalInOut(board.D26)
        self.buzzerPin.direction = digitalio.Direction.OUTPUT
        self.buzzerPin.value = True

    def SendTakeSignal(self):
        msg = bytes(self.uuid, " Take Signal", "utf-8")
        for i in range(10):
            self.rfm9x.send(msg)
            self.buzzerPin.value = True
            sleep(.05)
            self.buzzerPin.value = False
            # sleep for random fraction of seconds
            sleep(randint(1, 5) / 10) 
            


def main():
    device_uuid = str(uuid4())

    faker_radio = Radio(device_uuid)

    while(True):
         faker_radio.SendTakeSignal()


if __name__ == '__main__':
    main()