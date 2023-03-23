# present a set of methods for the transmitter to
# generate a UUID and share it to reciever. This creates
# a link between the two
from uuid import uuid4
# countio is only recognized on a cirucitpython installation
import countio
from yaml import load, FullLoader

# Safely fetch the UUID from storage. Device agnostic.
# returns a code and the uuid value on success.
# a code less than 0 also returns -1 for the code.
def get_UUID():
    device_uuid = -1
    code, file = get_config()
    if (code < 0):
        return device_uuid, code
    try:
        with open(file, 'r') as f:
            device_uuid = f.readlines()
            f.close()
    except Exception as e:
        print(e)
        code = -2
        return device_uuid, code
    
    if type(device_uuid) is not str:
        code = -3
        return device_uuid, code
    
    code = 0
    return device_uuid, code
    
# Generate a new UUID and save it. For the transmitter.
def generate_UUID():
    device_uuid = -1
    code, file = get_config()
    if (code < 0):
        return device_uuid, code

    device_uuid = str(uuid4())

    try:
        with open(file, 'w') as f:
            f.write(device_uuid)
            f.close()
    except Exception as e:
        print(e)
        code = -2
        return -1, code
    
    code = 0
    return device_uuid, code

# Get config data from the yaml file. Device agnostic.
# Currently, only data to get from config is the location
# of the txt file that the UUID is in.
# returns a code and uuid file location.
def get_config():
    try:
        with open("config.yaml", 'r') as f:
            config = load(f, Loader=FullLoader)
            device_uuid = config["uuid.txt"]
            f.close()
            return  device_uuid, 0
    except Exception as e:
        print(e)
        return -1, -1