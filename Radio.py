import board
import busio
import digitalio
import adafruit_rfm9x
import random
import string
import time
import uuid

PacketHeaderLen:int = len(str(uuid.uuid4()))
SyncStr    = "SYNC"
AckStr     = "ACK"
TakeSignal = "TAKE"
SyncTimeout = 0.3
TotalSyncWaitSeconds = 60.0
FindFrequencyListenTime = 2.0

class Radio():
    def __init__(self, isTransmitter:bool, dbg:bool, CE:str):
        self.spi    = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        if (CE == "CE0"):
            self.cs = digitalio.DigitalInOut(board.CE0)
        elif (CE == "CE1"):
            self.cs = digitalio.DigitalInOut(board.CE1)
        else:
            print("ERROR: INVALID CE [" + str(CE) + "].  Valid options are CE0 or CE1")
        self.reset  = digitalio.DigitalInOut(board.D25)
        self.freq   = 902.0
        self.isTransmitter = isTransmitter
        self.uuid:str = ""
        self.dbg = dbg

        self.rfm9x = None
        while self.rfm9x == None:
            self.rfm9x  = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.freq)

    def FindOpenFrequency(self):
        # listen for two seconds to see if there is any interference on this channel
        if self.dbg:
            print("\tFinding an open frequency.  Starting with 902 MHZ")

        while True:
            msg = self.rfm9x.receive(timeout=FindFrequencyListenTime)
            # if we recieved any data after 2 seconds
            if msg != None:
                # reset the chip, increase the frequency, and re-initialize the device
                self.rfm9x.reset()
                self.rfm9x = None
                self.freq += 1.0
                if self.freq < 928.0:
                    while self.rfm9x == None:
                        self.rfm9x = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.freq)
            else:
                if self.dbg:
                    print("\tFound open frequency: " + str(self.freq))
                break

            # if we didn't find a good frequency, choose a random one
            if self.freq == 928.0:
                self.freq = float(round(random.uniform(902, 928)))
                if self.dbg:
                    print("\tChoosing random frequency: " + str(self.freq))

                self.rfm9x.reset()
                self.rfm9x = None
                while self.rfm9x == None:
                    self.rfm9x = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.freq)
                break

    def FindFrequencyWithSync(self):
        if self.dbg:
            print("\tFinding an open frequency.  Starting with 902 MHZ")

        header = ""
        msg = ""
        while True:
            # listen for long enough that the transmitter would send 3 SYNC packets
            header, msg = self.ReceiveHeadedMessage(timeout=SyncTimeout*3, sendAck=False, needRightHeader=False)
            if header == None or msg != SyncStr:
                # reset the chip, increase the frequency, and re-initialize the device
                self.rfm9x.reset()
                self.rfm9x = None
                self.freq += 1.0
                # wrap back around to the legal frequencies
                if self.freq > 928.0:
                    self.freq = 902.0
                while self.rfm9x == None:
                    self.rfm9x  = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.freq)
            else:
                if self.dbg:
                    print("\tFound open frequency: " + str(self.freq))
                break

    # returns true if sync successful
    def Sync(self) -> bool:
        result = False
        # sync as transmitter
        # generate ID
        # send it
        # keep sending until we get an ACK,
        # send confirmation of ACK
        if self.isTransmitter:
            self.uuid = str(uuid.uuid4())
            self.FindOpenFrequency()
            # send a new sync packet every 0.5 seconds
            retries = int(TotalSyncWaitSeconds / SyncTimeout)
            result = self.SendHeadedMessage(message=SyncStr, withAck=True, ackTimeout=SyncTimeout, retries=retries)
            if self.dbg:
                if result == False:
                    print("Error: No Ack on sync... something went wrong")
                else:
                    print("Synced! uuid: " + self.uuid)

        #sync as receiver
        # listen for packet with msg = SYNC
        # set our UUID to what we got in the packet
        # send an ACK packet
        else:
            self.uuid = ""
            header = ""
            recMsg = ""
            self.FindFrequencyWithSync()
            while result == False:
                #we actually don't need the right header for this
                if self.dbg:
                    print("\tAttempting to sync as reciever")
                header, recMsg = self.ReceiveHeadedMessage(timeout = 1, infiniteLoop=True, needRightHeader=False)
                if None not in [header, recMsg]:
                    if (recMsg == SyncStr) and (len(header) == PacketHeaderLen):
                        result = True
            self.uuid = header
            if self.dbg:
                print("\tSuccessfully synced.  UUID: " + self.uuid)
            self.SendHeadedMessage(message=AckStr)

        return result

    def SendTakeSignal(self):
        if self.dbg:
            print("Sending Take Signal")
        gotAck = self.SendHeadedMessage(message=TakeSignal, withAck=True, retries=15, ackTimeout=1.0)
        if self.dbg:
            if gotAck == False:
                print("\tWarning, Ack not recieved!")
            else:
                print("\t Message sent and Ack received!")

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
                try:
                    recStr:str = recMsg.decode()
                except KeyboardInterrupt:
                    break
                except Exception as exc:
                    print("Exception: " + str(exc))
                    print("\t^This is probably bad radio packet... just go back to listening")
                    keepLooping = True
                    continue
                header, delim, msg = recStr.partition(":")
                # if we got a header and msg
                if "" not in [header, delim, msg]:
                    if needRightHeader:
                        if header == self.uuid:
                            if sendAck:
                                self.SendAck()
                            return (header, msg)
                        elif self.dbg:
                            print("Recieved Packet with different header!")
                            print("\tExpeced:  " + self.uuid)
                            print("\tRecieved: " + header)
                            print("\tMessage:  " + msg)
                    else:
                        return (header, msg)

                # if we didn't get one, return whole message in the msg section if we aren't looking
                # for headers
                else:
                    if self.dbg:
                        print("\tPacket no header received, all in msg")
                        print("\tMessage: " + header)
                    if needRightHeader == False:
                        return (None, header)
        return (None, None)

    def SendAck(self):
        if self.dbg:
            print("\tSending Ack!")
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
            if (self.dbg) and (retries > 1):
                print("\t\tAttempt: " + str(i) + "/" + str(retries))

            result:bool = self.rfm9x.send(msg, keep_listening=withAck)
            if withAck and result:
                # no ack yet
                result = False

                # add a little noise
                timeOut:float = ackTimeout + random.uniform(-0.1, 0.1)
                header, recMsg = self.ReceiveHeadedMessage(timeout=timeOut)
                if header == self.uuid and recMsg == AckStr:
                    if self.dbg:
                        print("\tGot ACK with correct header: " + header)
                    result = True
                    break
                elif header != None or recMsg != None:
                    if self.dbg:
                        print("Wrong header or msg (could be another device): ")
                        print("Header: " + str(header))
                        print("recMsg: " + str(recMsg))
            else:
                break
        return result