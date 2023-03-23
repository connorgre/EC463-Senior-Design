# EC463-Senior-Design
Take Notifier code

## Daniel's Implementation of Networking Plan:

From Logbook:

The current goals of the program is this:

1. Both transmitter and reciever start the Take Notifier Software on device boot.

2. Both transmitter and reciever check if they have a set uuid. If they don't, alert the user by activating the buzzer and light. The device then goes into sync mode.

3. If a uuid is found, the device goes into pairing check mode. The transmitter will begin transmitting its uuid, and will wait until it recieves a ACK message from a reciever It will send an ACK and notify the user that it has entered paired mode. The reciever waits for a message of uuid length (to parse out junk packets), and upon recieving one, compares it to its uuid. If they are identical, it broadcasts an ACK and waits for an ACK back. Upon recieving this ACK, it notifies the user and enters paired mode.

4. At any point, the user can force the devices into sync mode via a button press.

Modes Elaboration:

- Sync Mode: The mode to create and set a pair uuid. 

Transmitter: Generate and save a new uuid. Broadcast the uuid and await an ACK message that contains the uuid. Repeat this until the ACK has been recieved. Afterwards, send an additional ACK with the uuid and switch to paired mode. Physically notify the user of the successful device pairing.

Reciever: Await a packet with a message of only uuid length. Save the message's contents as the device's new uuid. Broadcast an ACK with the recieved uuid. Await an additional ACK with the uuid. Failure to recieve the second ACK after a set period of time physically alerts the user and returns the device to the start of sync mode. Successful detection of the second ACK switches the reciever to paired mode and notifies the user.

- Pair Check Mode:

Pair Check Mode is identical to Sync mode except that uuids are already present in the device's memories and are neither generated nor overwritten.

- Paired Mode:

Transmitter: Await wakeword detection. Upon detection, listen for packets until channel appears clear. Send 5 packets with the device uuid as contents and a random time interval between each packet.

Reciever: Await packet detection. Discard all packets that do not have the device uuid as contents. Notify the user upon successful detection of valid packet.

For a very rough state machine diagram see here:

https://drive.google.com/file/d/1sRZePLNZZAEJpbubDho8jZ6wpkWRUHtD/view?usp=sharing

https://drive.google.com/file/d/1ZfgOCjL0uc_8qV8tmPECuU5l78cJS29-/view?usp=sharing
