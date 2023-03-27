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
TakeSignal = "TAKE"

class Radio():
    def __init__(self, isTransmitter:bool, dbg:bool, frequency:float=915.0):
        self.spi    = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        self.cs     = digitalio.DigitalInOut(board.CE1)
        self.reset  = digitalio.DigitalInOut(board.D25)
        self.freq   = 915.0
        self.rfm9x  = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.freq)
        self.isTransmitter = isTransmitter
        self.uuid:str = ""
        self.dbg = dbg

    # returns true if sync successful
    def Sync(self) -> bool:

        result = False
        # sync as transmitter
        # generate ID
        # send it
        # keep sending until we get an ACK,
        # send confirmation of ACK
        if self.isTransmitter:
            self.uuid = ''.join(random.choices(string.ascii_letters, k=PacketHeaderLen))

            result = self.SendHeadedMessage(message=SyncStr, withAck=True, ackTimeout=2.0, retries=100)
            if result == False:
                print("Error: No Ack on sync... something went wrong")

        #sync as receiver
        # listen for packet with msg = SYNC
        # set our UUID to what we got in the packet
        # send an ACK packet
        else:
            self.uuid = ""
            header = ""
            recMsg = ""
            while result == False:
                #we actually don't need the right header for this
                header, recMsg = self.ReceiveHeadedMessage(timeout = 1, infiniteLoop=True, needRightHeader=False)
                if None not in [header, recMsg]:
                    if (recMsg == SyncStr) and (len(header) == PacketHeaderLen):
                        result = True
            self.uuid = header
            self.SendHeadedMessage(message=AckStr)

        return result

    def SendTakeSignal(self):
        for _ in range(10):
            self.SendHeadedMessage(message=TakeSignal)
            self.sleep(.1 + random.uniform(-0.025, 0.025))

    # returns (header, msg, correctHeader) tuple, if no header is detected
    # whole thing is in msg, else, both are none.
    # set infiniteLoop to continuously listen
    def ReceiveHeadedMessage(self,
                             timeout:float=1.0,
                             sendAck:bool=True,
                             maxRetries:int=0,
                             infiniteLoop:bool=False,
                             needRightHeader:bool=True) -> "tuple[str, str]":
        keepLooping:bool = True
        numLoops:int = 0
        while keepLooping:
            numLoops += 1
            if ((numLoops > maxRetries) and (infiniteLoop == False)):
                keepLooping = False

            recMsg = self.rfm9x.receive(timeout=timeout)
            if recMsg != None:
                recStr:str = recMsg.decode()
                header, delim, msg = recStr.partition(":")
                # if we got a header and msg
                if "" not in [header, delim, msg]:
                    if needRightHeader:
                        if header == self.uuid:
                            if sendAck:
                                self.SendAck()
                            return (header, msg)
                        elif self.dbg:
                            print ("Error: Header wrong!!")
                    else:
                        return (header, msg)

                #if we didn't get one, return whole message in the msg section
                else:
                    if self.dbg:
                        print("Error: No Header received, all in msg")
                    return (None, header)
        return (None, None)

    def SendAck(self):
        self.SendHeadedMessage(message=AckStr)

    # returns false if we didn't get an ack and wanted one
    def SendHeadedMessage(self,
                          message:str,
                          withAck:bool=False,
                          ackTimeout:float=1.0,
                          retries:int=5) -> bool:
        assert(self.uuid != "")
        assert(len(self.uuid) == PacketHeaderLen)

        msg = bytes(self.uuid + ":" + message, "utf-8")
        result = False

        # retries needs to be at least 1 so we send the first message
        if retries <= 0:
            retries = 1

        for i in range(retries):
            result:bool = self.rfm9x.send(msg, keep_listening=withAck)
            if withAck and result:
                header, recMsg = self.ReceiveHeadedMessage(timeout=ackTimeout)
                if header == self.uuid and recMsg == AckStr:
                    if self.dbg:
                        print("Got ACK with correct header: " + header)
                    return True
                elif header != None or recMsg != None:
                    if self.dbg:
                        print("Wrong header or msg:")
                        print("Header: " + str(header))
                        print("recMsg: " + str(recMsg))
            else:
                break
        return result

class Receiver:
    def __init__(self, dbg:bool):
        self.radio = Radio(isTransmitter=False, dbg=dbg)
        self.buzzerPin = digitalio.DigitalInOut(board.D26)
        self.dbg = dbg

        self.buzzerPin.direction = digitalio.Direction.OUTPUT
        self.buzzerPin.value = True
        if (dbg):
            print("init receiver, buzz*3")
            for i in range(3):
                self.Buzz(0.5)

    def Sync(self):
        result = self.radio.Sync()
        if self.dbg:
            print("Receiver sync status: " + str(result))

    def Buzz(self, buzzTime:float = 0.5):
        if self.dbg:
            print("Buzzing for: " + str(buzzTime))
        self.buzzerPin.value = False
        time.sleep(buzzTime)
        self.buzzerPin.value = True

    def EnterListenLoop(self):
        while True:
            try:
                header, msg = self.radio.ReceiveHeadedMessage(timeout=5.0,
                                                                sendAck=False,
                                                                needRightHeader=True,
                                                                infiniteLoop=True)
                if self.dbg:
                    print("Header: " + header)
                    print("Msg:    " + msg)
                if msg == TakeSignal:
                    self.Buzz(3.0)
            except Exception as exc:
                print("Exiting bc: " + str(exc))
                break

