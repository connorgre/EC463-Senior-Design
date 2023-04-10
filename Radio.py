import board
import busio
import digitalio
import adafruit_rfm9x
import random
import string
import time
import uuid
from threading import Thread
from LED import *

PacketHeaderLen         :int   = len(str(uuid.uuid4()))
# packet to signal that a sync is wanted
SyncStr                 :str   = "SYNC"
# Acknoledgement packet
AckStr                  :str   = "ACK"
# Signal that Take has been detected
TakeSignal              :str   = "TAKE"
# Signal to send noise on frequency so other radios won't try to use this one
NoiseStr                :str   = "NOISE"
SyncTimeout             :float = 0.3
TotalSyncWaitSeconds    :float = 60.0

FindFrequencyListenTime:float  = 2.0
AllowedFrequencies:"list[float]" = [float(x) for x in range(902, 928, 4)]

class Radio():
    def __init__(self, isTransmitter:bool, dbg:bool, frequency:float=915.0):
        self.spi    = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        self.reset  = digitalio.DigitalInOut(board.D25)
        self.freq   = 915.0
        self.isTransmitter = isTransmitter
        self.uuid:str = ""
        self.dbg = dbg

        self.rfm9x = None
        self.cs = digitalio.DigitalInOut(board.CE0)

        self.ConnectToRadio()

    def ConnectToRadio(self):
        # cycle through the CE pins until we are able to sync to the board
        nextCEtoTry = 0
        connected = False
        firstTry = False
        # silently try with current CE pin without printing anything
        if self.rfm9x != None:
            self.rfm9x.reset()

        try:
            self.rfm9x  = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.freq)
            connected = True
            firstTry = True
        except Exception as e:
            if self.dbg:
                print("Exception: " + str(e))
                print("            ^This is expected to maybe happen once or twice.")
            connected = False

        while connected == False:
            if (self.dbg):
                print("\tAttempting to connect to radio")
            if nextCEtoTry == 0:
                self.cs = digitalio.DigitalInOut(board.CE0)
                nextCEtoTry = 1
            else:
                self.cs = digitalio.DigitalInOut(board.CE1)
                nextCEtoTry = 0
            try:
                self.rfm9x  = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.freq)
                connected = True
            except Exception as e:
                if self.dbg:
                    print("Exception: " + str(e))
                    print("            ^This is expected to maybe happen once or twice.")
                connected = False

        ceUsed = 0 if (nextCEtoTry == 1) else 1
        if self.dbg and (firstTry == False):
            print("\tSuccessfully paired with radio.  CE: " + str(ceUsed))

    def FindOpenFrequency(self):
        # listen for two seconds to see if there is any interference on this channel
        if self.dbg:
            print("\tFinding an open frequency.  Starting with 902 MHZ")

        # want to start at a random frequency to avoid all radios clogging the lower ones
        # if there is more than one
        startFreq = random.randrange(len(AllowedFrequencies))
        freqFound = False
        for freq in AllowedFrequencies[startFreq:] + AllowedFrequencies[:startFreq]:
            # reset the device with the new frequency
            self.freq = freq
            self.ConnectToRadio()

            # send some noise to stop other radios from trying to use this frequency
            self.SendNoise()
            msg = self.rfm9x.receive(timeout=FindFrequencyListenTime)
            if msg == None:
                self.SendNoise()
                if self.dbg:
                    print("\tFound open frequency: " + str(self.freq))
                freqFound = True
                break

        # if we didn't find a good frequency, choose a random one
        if freqFound == False:
            self.freq = random.choice(AllowedFrequencies)
            if self.dbg:
                print("\tChoosing random frequency: " + str(self.freq))

            self.rfm9x.reset()
            self.rfm9x = None
            while self.rfm9x == None:
                self.rfm9x = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.freq)
            # just send some noise in case another radio is also currently looking on this frequency
            self.SendNoise()

    def FindFrequencyWithSync(self):
        if self.dbg:
            print("\tFinding an open frequency.  Starting with 902 MHZ")

        foundFreq = False
        # continuously loop through frequencies looking for sync packet
        while foundFreq == False:
            for freq in AllowedFrequencies:
                print("Checking Frequency: " + str(freq))
                self.freq = freq
                self.ConnectToRadio()

                # wait for double length of SyncTimeout to guarantee at least 1 packet will be sent
                header, msg = self.ReceiveHeadedMessage(timeout=SyncTimeout*2, sendAck=False, needRightHeader=False)

                if (header != None) and (msg == SyncStr):
                    if self.dbg:
                        print("\tFound open frequency: " + str(self.freq))
                    foundFreq = True
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
            whileSyncingLEDs()
            result = self.SendHeadedMessage(message=SyncStr, withAck=True, ackTimeout=SyncTimeout, retries=retries)
            if self.dbg:
                if result == False:
                    print("Error: No Ack on sync... something went wrong")
                else:
                    print("Synced! uuid: " + self.uuid)
                if result == False:
                    noSyncLEDs()

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
                whileSyncingLEDs()
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
            syncedLEDs()

        if result
        return result

    def SendTakeSignal(self):
        if self.dbg:
            print("Sending Take Signal")
        msgSentLEDs()
        gotAck = self.SendHeadedMessage(message=TakeSignal, withAck=True, retries=15, ackTimeout=1.0)
        if self.dbg:
            if gotAck == False:
                print("\tWarning, Ack not recieved!")
            else:
                print("\t Message sent and Ack received!")
        if gotAck == False:
            outOfBoundsLEDs()

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

    def SendNoise(self):
        if self.dbg:
            print("\tSending Noise")
        self.SendHeadedMessage(message=NoiseStr)

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
