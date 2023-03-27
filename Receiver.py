from Radio import *

def main():

    device = Reciever(True)
    device.Sync()
    device.EnterListenLoop()
    return

if __name__=="__main__":
    main()