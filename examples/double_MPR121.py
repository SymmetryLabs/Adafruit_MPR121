# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import sys
import time

import argparse
import random
import time

from pythonosc import osc_message_builder
from pythonosc import udp_client


import Adafruit_MPR121.MPR121 as MPR121

parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="127.0.0.1",
    help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=3030,
    help="The port the OSC server is listening on")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)

print('Adafruit MPR121 Capacitive Touch Sensor Test')

# Create MPR121 instance.
cap0 = MPR121.MPR121()
cap1 = MPR121.MPR121()

# Initialize communication with MPR121 using default I2C bus of device, and
# default I2C address (0x5A).  On BeagleBone Black will default to I2C bus 0.
# if not cap.begin():
#     print('Error initializing MPR121.  Check your wiring!')
#     sys.exit(1)

# Alternatively, specify a custom I2C address such as 0x5B (ADDR tied to 3.3V),
# 0x5C (ADDR tied to SDA), or 0x5D (ADDR tied to SCL).
def init_both():
    if not cap0.begin(address=0x5C):
        print('Error initializing MPR121 one')
        sys.exit(1)

    if not cap1.begin(address=0x5D):
        print('Error initializing MPR121 two')
        sys.exit(1)

init_both()

# Also you can specify an optional I2C bus with the bus keyword parameter.
#cap.begin(busnum=1)


def both_touched():
    return [cap0.touched(), cap1.touched()]

def fmtSendOsc(label, enum_list):
    for i, elt in enumerate(enum_list):
        client.send_message("/touch/" + label + "/" + str(i), elt)
        # print(elt)

# Main loop to print a message every time a pin is touched.
print('Press Ctrl-C to quit.')
# import pdb; pdb.set_trace()
last_touched = both_touched()


while True:
    try:
        current_touched = both_touched()
        # Check each pin's last and current state to see if it was pressed or released.
        for cap in range(2):
            for i in range(12):
                # Each pin is represented by a bit in the touched value.  A value of 1
                # means the pin is being touched, and 0 means it is not being touched.
                pin_bit = 1 << i
                # First check if transitioned from not touched to touched.
                if current_touched[cap] & pin_bit and not last_touched[cap] & pin_bit:
                    print('{0} touched!'.format(i + cap*12))
                # Next check if transitioned from touched to not touched.
                if not current_touched[cap] & pin_bit and last_touched[cap] & pin_bit:
                    print('{0} released!'.format(i + cap*12))
        # Update last state and wait a short period before repeating.
        last_touched = current_touched
        time.sleep(0.1)

        # Alternatively, if you only care about checking one or a few pins you can
        # call the is_touched method with a pin number to directly check that pin.
        # This will be a little slower than the above code for checking a lot of pins.
        #if cap.is_touched(0):
        #    print('Pin 0 is being touched!')

        # If you're curious or want to see debug info for each pin, uncomment the
        # following lines:
        #print '\t\t\t\t\t\t\t\t\t\t\t\t\t 0x{0:0X}'.format(cap.touched())
        # filtered = [cap.filtered_data(i) for i in range(12)]
        # fmtSendOsc("filtered", filtered)
        # # print("------")

        # # print('FILT:', '\t'.join(map(str, filtered))),
        # base = [cap.baseline_data(i) for i in range(12)]
        # fmtSendOsc("base", base)
        # print('BASE:', '\t'.join(map(str, base)))
        # client.send_message("/lx/output/enabled", filtered)
    except:
        print ("exceeption occured, ignoring to keep sensing")
