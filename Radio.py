import board
import busio
import digitalio
import adafruit_rfm9x
import random
import string
import time

PacketHeaderLen:int = 16
SyncStr    = "SYNC"
AckStr     = "ACK"

class Radio():
    def __init__(self, isTransmitter:bool):
        self.spi    = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        self.cs     = digitalio.DigitalInOut(board.CE1)
        self.reset  = digitalio.DigitalInOut(board.D25)
        self.freq   = 915.0
        self.rfm9x  = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.freq)
        self.isTransmitter = isTransmitter
        self.uuid:str = ""

    def sync(self):
        if self.isTransmitter:
            self.uuid = ''.join(random.choices(string.ascii_letters, k=PacketHeaderLen))

            gotAck = False
            msg = bytes(self.uuid + ":" + SyncStr, "utf-8")
            while gotAck == False:
                self.rfm9x.send(msg)
                recMsg = self.rfm9x.receive()
                if recMsg != None:
                    recStr = recMsg.decode()
                    print("Recieved: " + recStr)

    def SendTakeSignal(self):
        msg = bytes("Take Signal", "utf-8")
        for i in range(10):
            self.rfm9x.send(msg)
            time.sleep(.1)

    # returns (header, msg, correctHeader) tuple, if no header is detected
    # whole thing is in msg, else, both are none.
    # set infiniteLoop to continuously listen
    def RecieveHeadedMessage(self,
                             timeout:float=1.0,
                             sendAck:bool=False,
                             maxRetries:int=0,
                             infiniteLoop:bool=False,
                             dbg:bool=True) -> tuple(str, str):
        keepLooping:bool = True
        numLoops:int = 0
        while keepLooping:
            numLoops += 1
            if ((numLoops > maxRetries) and (infiniteLoop == False)):
                keepLooping = False

            recMsg = self.rfm9x.recieve(timeout=timeout)
            if recMsg != None:
                recStr:str = recMsg.decode()
                header, delim, msg = recStr.partition(":")
                # if we got a header and msg
                if "" not in [header, delim, msg]:
                    if header == self.uuid:
                        if sendAck:
                            self.SendAck(dbg=dbg)
                    elif dbg:
                        print ("Error: Header length wrong!!")

                    return (header, msg)
                #if we didn't get one, return whole message in the msg section
                else:
                    if dbg:
                        print("Error: No Header recieved, all in msg")
                    return (None, header)
        return (None, None)

    def SendAck(self, dbg:bool=True):
        self.SendHeadedMessage(message=AckStr, dbg=dbg)

    # returns false if we didn't get an ack and wanted one
    def SendHeadedMessage(self,
                          message:str,
                          withAck:bool=False,
                          ackTimeout:float=1.0,
                          dbg:bool=True,
                          retries:int=5) -> bool:
        assert(self.uuid != "")
        assert(len(self.uuid) == PacketHeaderLen)

        msg = bytes(self.uuid + ":" + message)
        result = False

        # retries needs to be at least 1 so we send the first message
        if retries <= 0:
            retries = 1

        for i in range(retries):
            result:bool = self.rfm9x.send(msg, keep_listening=withAck)
            if withAck and result:
                header, recMsg = self.RecieveHeadedMessage(timeout=ackTimeout, dbg=dbg)
                if header == self.uuid and recMsg == AckStr:
                    if dbg:
                        print("Got ACK with correct header: " + header)
                    return True
                elif header != None or recMsg != None:
                    if dbg:
                        print("Wrong header or msg:")
                        print("Header: " + str(header))
                        print("recMsg: " + str(recMsg))
            else:
                break
        return result