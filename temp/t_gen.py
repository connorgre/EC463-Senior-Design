# Goal of program: Initiate a system to create
# a random large number that a transmitter
# and reciever can use to identify their
# paired device
from random import randint
import os

# generate a trio of large numbers to use as a device
# identifer. Deletes existing numbers and r
def gen_pair_num():
    
    # generate random numbers
    num_1 = randint(0,2147483647)
    num_2 = randint(0,2147483647)
    num_3 = randint(0,2147483647)
    num_list = {num_1, num_2, num_3}

    #write down in a text file
    # overwrite pair_num.csv
    try:
        f = open("pair_num.csv", "w")
        f.write(num_1, ',', num_2, ',', num_3)
        f.close()
    except:
        print("An exception occured")
        return -1
    
    #send to reciever
    def sync_num(num_list)
    #timeout if necessary
    return 0

def get_pair_num():
    # search for text file
    num_list = {}
    try:
        path = "pair_num.csv"
        if path.exists():
            f = open("pair_num.csv", os.O_RDONLY)
            # get values from text file
            nums = f.read(14)
            num_list = nums.split(',')
            f.close()
    except:
        print("An exception occured")
        return -1

    # send number to reciever to check (USE SYNC)
    sync_num(num_list)

    return 0

def sync_num(num_list):
    #attempt 5 times
    for i in range(5):
        #send num_list
        print("sending numbers to the reciever...")

        #wait for ACK 
    
    return -1
