from Radio import *

def main():

    device = Receiver(True)
    device.Sync()
    device.EnterListenLoop()
    return

if __name__=="__main__":
    main()