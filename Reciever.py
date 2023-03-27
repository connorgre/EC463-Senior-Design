from Radio import *

def main():

    device = Reciever()
    device.Sync()
    device.EnterListenLoop()
    return

if __name__=="__main__":
    main()