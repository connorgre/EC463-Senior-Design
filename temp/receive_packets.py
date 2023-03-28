import board
import busio
import digitalio
import adafruit_rfm9x
import time

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO = board.MISO)

cs = digitalio.DigitalInOut(board.CE0)
reset = digitalio.DigitalInOut(board.D25)

num = 0
err = True

while err:
    err = False
    try:
        rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0)
    except RuntimeError as error:
        err = True
        if num % 100 == 0:
            print("Error: ", err)
        num+= 1
    time.sleep(.1)

print("num tries: ", num)

while True:
    packet = rfm9x.receive()
    if packet is not None:
        print("Raw bytes: {0}".format(packet))
        packetTxt = str(packet, "utf-8")
        print("After decode: ", packetTxt)
