import board
import busio
import digitalio
import adafruit_rfm9x
import time

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.CE0)
reset = digitalio.DigitalInOut(board.D25)
freq = 915.0

rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, freq)

buzzerPin = digitalio.DigitalInOut(board.D26)
buzzerPin.direction = digitalio.Direction.OUTPUT
buzzerPin.value = True
for i in range(5):
    print("should blink")
    buzzerPin.value = False
    time.sleep(.5)
    buzzerPin.value = True
    time.sleep(.5)

print('listening')
while True:
    msg = rfm9x.receive()
    if msg is not None:
        print(msg)
        buzzerPin.value = False
        time.sleep(1)
        buzzerPin.value = True
