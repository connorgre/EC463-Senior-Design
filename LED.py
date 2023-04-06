# Helper module for running threadable LED code
# LED functions are intended to be threadable so that
# They can illuminate independently of other operations
# like sending packets.
import digitalio
import board
import time

# Constants for LED pins. Alterable.
LED1 = board.D2
LED2 = board.D3

# short set of both LEDs flashing to denote device activation
def onBootLEDs():
    led1 = digitalio.DigitalInOut(LED1)
    led2 = digitalio.DigitalInOut(LED2)
    led1.direction = digitalio.Direction.OUTPUT
    led2.direction = digitalio.Direction.OUTPUT

    for i in range(2):
        led1.value = True
        led2.value = True
        time.sleep(.1)
        led1.value = False
        led2.value = False
        time.sleep(.1)

# short flicker to repeatedly occur while devices are syncing
# to be called repeatedly and thus has no internal loop
def whileSyncingLEDs():
    led1 = digitalio.DigitalInOut(LED1)
    led2 = digitalio.DigitalInOut(LED2)
    led1.direction = digitalio.Direction.OUTPUT
    led2.direction = digitalio.Direction.OUTPUT
    
    led1.value = True
    time.sleep(.1)
    led2.value = True
    led1.value = False
    time.sleep(.1)
    led2.value = False

# Long wait to denote devices are synced and ready to function
def syncedLEDs():
    led1 = digitalio.DigitalInOut(LED1)
    led2 = digitalio.DigitalInOut(LED2)
    led1.direction = digitalio.Direction.OUTPUT
    led2.direction = digitalio.Direction.OUTPUT

    led1.value = True 
    led2.value = True
    time.sleep(1)
    led1.value = False
    led2.value = False     

# short symbol to denote that a message was detected and sent
def msgSentLEDs():
    led1 = digitalio.DigitalInOut(LED1)
    led1.direction = digitalio.Direction.OUTPUT

    for i in range(3):
        led1.value = True
        time.sleep(.3)
        led1.value = False

# aggressive and long duration flickering to catcher belayer's attention
# that it is time to Take Up
def msgReceivedLEDs():
    led1 = digitalio.DigitalInOut(LED1)
    led2 = digitalio.DigitalInOut(LED2)
    led1.direction = digitalio.Direction.OUTPUT
    led2.direction = digitalio.Direction.OUTPUT
    
    for i in range(5):
         led1.value = True
         led2.value = True
         time.sleep(.5)

         led1.value = False
         led2.value = False

         for i in range(3):
            led1.value = True
            time.sleep(.1)
            led2.value = True
            led1.value = False
            time.sleep(.1)
            led2.value = False

 