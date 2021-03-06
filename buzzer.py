#!/usr/bin/env python3
"""
buzzer.py
~~~~~~~~
Python based apartment style buzzer for the Raspberry Pi
"""

import os
import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime

# Pins (BCM) https://pinout.xyz/
button_pin = 4
red_pin = 25
green_pin = 24
blue_pin = 23

# Variables
buttonHoldDuration = 1

# GPIO Setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(red_pin, GPIO.OUT)
GPIO.setup(green_pin, GPIO.OUT)
GPIO.setup(blue_pin, GPIO.OUT)

buttonPressedTime = None
def buttonStateChanged(pin):
    """ Defines Button Press Event """
    global buttonPressedTime
    if not (GPIO.input(pin)):
        if buttonPressedTime is None:
            GPIO.output(red_pin, False)
            GPIO.output(green_pin, False)
            GPIO.output(blue_pin, False)
            buttonPressedTime = datetime.now()
    else:
        if buttonPressedTime is not None:
            elapsed = (datetime.now() - buttonPressedTime).total_seconds()
            buttonPressedTime = None
            if elapsed >= buttonHoldDuration:
                # prompt user
                GPIO.output(green_pin, True)
                os.system('mpg123 -q ./sounds/whos_there.mp3 &')
                sleep(1.25)
                GPIO.output(green_pin,False)
                # indicate recording with red
                os.system('arecord -d 2 -f S16_LE -r 41000 ./sounds/recent_greeting.wav &')
                GPIO.output(red_pin, True)
                sleep(2)
                GPIO.output(red_pin, False)
                # indicate playback with blue
                GPIO.output(blue_pin, True)
                os.system('aplay -d 2 -f S16_LE -r 41000 ./sounds/recent_greeting.wav &')
                sleep(2)
                GPIO.output(blue_pin, False)

            elif elapsed < buttonHoldDuration:
                GPIO.output(blue_pin, True)
                os.system('mpg123 -q ./sounds/doorbuzz.mp3 &')
                sleep(.2)
                GPIO.output(blue_pin, False)

try:
    print("[Buzzer Active] CTRL-C to Quit")
    GPIO.add_event_detect(button_pin, GPIO.BOTH, callback=buttonStateChanged)
    while True:
        sleep(1)

except KeyboardInterrupt:
    print("\n")

finally:
    GPIO.output(red_pin, False)
    GPIO.output(green_pin, False)
    GPIO.output(blue_pin, False)
    GPIO.cleanup()
