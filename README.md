# Boston University 2022-2023 Senior Design: Team 7, "Take Notifier"

## Contributors: Ethan Klein, Kira Milgrim, Brandon Swain, Connor Greenwood, & Daniel Paganelli

## Overview

The Take Notifier is a harness-mounted device system designed to improve the safety and acessibility of 
rock climbing. Each Take Notifier system is comprised of two devices, a transmitter and receiver, that
communicate over long range radio to ensure that simple rock climbing commands can be transferred between
an individual at the top of a climbing rope and their belayer. The Take Notifier is completely hands-free and
utilizes voice detection software to allow users to simply speak into a microphone in order to relay a message.
On the other side of the system, the belayer is alerted of a message, typically "Take Up", via their device lighting
up and vibrating.

## Transmitter

## Receiver

## Porcupine Audio

Porcupine Audio is a lightweight voice detection software that does not require connection to external servers to run. This
makes it perfect for rock climbers, who may find themselves miles from the nearest wi-fi network. Porcupine offers the ability
to designate "wake words", which execute further commands on detection. This functionality is used to make detection of "Take Up"
send a radio package.

Despite its lightweight nature, Porcupine is still accurate at detecting specifically the wake word. Speaking "Make up", "Fake up",
"Take Hup", or other similar but incorrect statements is exceedingly unlikely to trigger the voice detection software.

## Notes

Take Notifiers come "out of the box" with scripts to begin running their programs on boot. To run the receiver code manually,
use the command:

```
python3 Receiver.py
```

To run the Transmitter, run:
```
python3 Transmitter.py --access_key ${ACCESS_KEY} --keyword_paths ~/ake-up_en_raspberry-pi_v2_1_0.ppn --input_device_index 1
```
