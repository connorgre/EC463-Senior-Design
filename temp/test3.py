import time
import spidev

bus = 0

device = 0

spi = spidev.SpiDev()

spi.open(bus, device)

spi.max_speed_hz = 5000

spi.mode = 0

msg = [0xFF, 0xAA, 0x99, 0x12]

try:
  while True:
    spi.writebytes(msg)
    time.sleep(.01)
except KeyboardInterrupt:
  print("done")
