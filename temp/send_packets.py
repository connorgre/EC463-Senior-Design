import board
import busio
import digitalio
import adafruit_rfm9x
import time

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

cs = digitalio.DigitalInOut(board.CE1) # Currently this board is hooked up to CE1, change to CE0 
reset = digitalio.DigitalInOut(board.D25)

num = 0
err = True
while err:
    err = False
    try:
        rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0)
    except RuntimeError as error:
        err = True
        print("Error: ", error)
        num += 1
    time.sleep(.1)

print("num tries: ", num)

msg = bytes("Hello word! Sent from Raspberry pi 2!", "utf-8")

for i in range (100):
    rfm9x.send(msg)
    time.sleep(1)
print("Done!")
