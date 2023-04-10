# Helper module for running threadable LED code
# LED functions are intended to be threadable so that
# They can illuminate independently of other operations
# like sending packets.
import digitalio
import board
import time

# Constants for LED pins. Alterable.
LED1 = board.D12
LED2 = board.D13

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
    forceShutOffLEDs()

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
    forceShutOffLEDs()

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
    forceShutOffLEDs()

# short symbol to denote that a message was detected and sent
def msgSentLEDs():
    led1 = digitalio.DigitalInOut(LED1)
    led1.direction = digitalio.Direction.OUTPUT

    for i in range(3):
        led1.value = True
        time.sleep(.3)
        led1.value = False
    forceShutOffLEDs()

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
    forceShutOffLEDs()

# periodic beep to report no ACKs
#def outOfBoundsLEDs():


# periodic beep to report no sync
def noSyncLEDs():
    led1 = digitalio.DigitalInOut(LED1)
    led2 = digitalio.DigitalInOUT(LED2)
    led1 = digitalio.Direction.OUTPUT
    led1 = digitalio.Direction.OUTPUT
    led1.value = False
    led2.value = False

    for i in range(2):
        led1.value = True
        time.sleep(.3)
        led2.value = True
        led1.value = False
        time.sleep(.3)
        led2.value = False
    
    forceShutOffLEDs()

# Force turnoff to keep lights controlled
def forceShutOffLEDs():
    led1 = digitalio.DigitalInOut(LED1)
    led2 = digitalio.DigitalInOut(LED2)
    led1.direction = digitalio.Direction.OUTPUT
    led2.direction = digitalio.Direction.OUTPUT
    led1.value = False
    led2.value = False

def main():
    print(dir(board))
    led1 = digitalio.DigitalInOut(LED1)
    led2 = digitalio.DigitalInOut(LED2)
    led1.direction = digitalio.Direction.OUTPUT
    led2.direction = digitalio.Direction.OUTPUT
    print("Running Light Test...")
    while(1):
        led1.value = True
        led2.value = True
        print('On...')
        time.sleep(1)
        led1.value = False
        led2.value = False
        print('Off...')
        time.sleep(1)
        forceShutOffLEDs()

if __name__=="__main__":
    main()
