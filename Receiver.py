from Radio import *

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
                                                                sendAck=True,
                                                                needRightHeader=True,
                                                                infiniteLoop=True)
                if self.dbg:
                    print("Header: " + header)
                    print("Msg:    " + msg)
                if msg == TakeSignal:
                    self.Buzz(buzzTime=3.0)
            except Exception as exc:
                print("Exiting bc: " + str(exc))
                break



def main():

    device = Receiver(dbg=True)
    device.Sync()
    device.EnterListenLoop()
    return

if __name__=="__main__":
    main()