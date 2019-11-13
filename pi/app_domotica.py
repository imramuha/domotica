from sense_hat import SenseHat
from time import time, sleep
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore
import os
import sys
import random
import json
from math import floor, ceil

# constants
RB = (254, 0, 0)
GB = (0, 254, 0)
RF = (255, 0, 0)
GF = (0, 255, 0)
B = (0, 0, 255)
Y = (255, 255, 68)
DB = (0, 0, 68)
DY = (68, 68, 0)
O = (0, 0, 0)

# Room
room = [
    GF, GF, GF, O, B, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, Y, O, O, O, Y,
    B, O, O, O, O, O, O, O,
    B, O, O, O, O, O, O, O,
    O, O, O, Y, O, O, O, Y,
    O, O, O, O, O, O, O, O,
    GB, GB, GB, O, B, O, O, O
]


# SenseHat
try:
    sense_hat = SenseHat()
    sense_hat.set_imu_config(False, False, False)

except:
    print('Unable to initialize the Sense Hat library: {}'.format(
        sys.exc_info()[0]))
    sys.exit(1)

# firebase implementation
try:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL':  'https://domotica-fda03.firebaseio.com'
    })

    root = db.reference('room')

except:
    print('Error with DB! Stopping the application...')
    sys.exit(1)


def main():
    while True:
        # Room - cbf making a function for it
        # Light
        if root.child('lights').get() == 'on':
            room[:] = [Y if x == DY else x for x in room]            
        elif root.child('lights').get() == 'off':
            room[:] = [DY if x == Y else x for x in room]

        # Outlets
        if root.child('outlets').get() == 'on':
            room[:] = [B if x == DB else x for x in room]
        elif root.child('outlets').get() == 'off':
            room[:] = [DB if x == B else x for x in room]

        # Backdoor
        if root.child('backdoor').get() == 'on':
            room[:] = [GB if x == RB else x for x in room]
        elif root.child('backdoor').get() == 'off':
            room[:] = [RB if x == GB else x for x in room]

        # Frontdoor
        if root.child('frontdoor').get() == 'on':
            room[:] = [GF if x == RF else x for x in room]
        elif root.child('frontdoor').get() == 'off':
            room[:] = [RF if x == GF else x for x in room]

        # Alert
        if root.child('alert').get() == 'on':
            color = [DY, Y]
            room[:] = [random.choice(color) if x == Y or x == DY else x for x in room]
            room[:] = [GB if x == RB else x for x in room]
            room[:] = [GF if x == RF else x for x in room]

        sense_hat.set_pixels(room)

        # Temperature & humidity
        humidity = round(sense_hat.get_humidity())
        temp = round(sense_hat.get_temperature())
        db.reference('room').update({
            'temperature': temp,
            'humidity': humidity
        })
        print(humidity)

        sleep(3)
        print(temp)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print('Interrupt received! Stopping the application...')
    finally:
        print('Cleaning up the mess...')
        sys.exit(0)
