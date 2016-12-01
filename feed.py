###########################################################################################
# petfeeder.py v 1.0
#
# Author: Krish Sivakumar
# Created Dec 2015
#
# Program to automate on-demand pet feeding through the internet
# Uses Raspberry Pi as a controller
#
# Distributed under Creative Commons Attribution-NonCommercial-Sharealike licensing
# https://creativecommons.org/licenses/by-nc-sa/3.0/us/
#
############################################################################################


import time
import os
import sys
import RPi.GPIO as GPIO
from Adafruit_CharLCD import Adafruit_CharLCD
import httplib2
import json
import html2text


DEBUG = False
MOTORON = True
CHUCKNORRIS = False
NUMBERTRIVIA = True

# Here is our logfile
LOGFILE = "/tmp/petfeeder.log"

# GPIO pins for feeder control
MOTORCONTROLPIN = 19
FEEDBUTTONPIN = 6
RESETBUTTONPIN = 13

# Variables for feeding information
readyToFeed = False # not used now but for future use
feedInterval = 28800 # This translates to 8 hours in seconds
FEEDFILE="/home/petfeeder/lastfeed"
cupsToFeed = 1
motorTime = cupsToFeed * 27 # It takes 27 seconds of motor turning (~1.75 rotations) to get 1 cup of feed
<<<<<<< HEAD
=======

    
# Function to check email
def checkmail():
    global lastEmailCheck
    global lastFeed
    global feedInterval
>>>>>>> refs/remotes/origin/master
    

def buttonpressed(PIN):
    # Check if the button is pressed
    global GPIO
    
    # Cheap (sleep) way of controlling bounces / rapid presses
    time.sleep(0.2)
    button_state = GPIO.input(PIN)
    if button_state == False:
        return True
    else:
        return False


def printlcd(row, col, LCDmesg):
    # Set the row and column for the LCD and print the message
    global logFile
    global lcd
    
    lcd.setCursor(row, col)
    lcd.message(LCDmesg)


def feednow():
    # Run the motor for motorTime, messages in the LCD during the feeeding
    global GPIO
    global MOTORCONTROLPIN
    global motorTime
    global lastFeed

    lcd.clear()
    printlcd(0,0,"Feeding now.....")
    if MOTORON:
        GPIO.output(MOTORCONTROLPIN, True)
        time.sleep(motorTime)
        GPIO.output(MOTORCONTROLPIN, False)
        printlcd(0,1, "Done!")
        time.sleep(2)
    return time.time()

def saveLastFeed():
    global FEEDFILE
    global lastFeed
    with open(FEEDFILE, 'w') as feedFile:
        feedFile.write(str(lastFeed))
    feedFile.close()


# This is the main program, essentially runs in a continuous loop looking for button press or remote request
try:

    #### Begin initializations #########################
    ####################################################
    
    # Initialize the logfile
    logFile = open(LOGFILE, 'a')

    # Initialize the LCD
    lcd = Adafruit_CharLCD()
    lcd.begin(16,2)
    lcd.clear()

    # Initialize the GPIO system
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # Initialize the pin for the motor control
    GPIO.setup(MOTORCONTROLPIN, GPIO.OUT)
    GPIO.output(MOTORCONTROLPIN, False)

    # Initialize the pin for the feed and reset buttons
    GPIO.setup(FEEDBUTTONPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(RESETBUTTONPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Initialize lastFeed
    if os.path.isfile(FEEDFILE):
        with open(FEEDFILE, 'r') as feedFile:
            lastFeed = float(feedFile.read())
        feedFile.close()
    else:
        lastFeed = time.time()
        saveLastFeed()
        

    #### End of initializations ########################
    ####################################################

    #### The main loop ####
    
    while True:

        #### If reset button pressed, then reset the counter
        if buttonpressed(RESETBUTTONPIN):
            lcd.clear()
            printlcd(0,0, "Resetting...   ")
            time.sleep(2)
            lastFeed = time.time() - feedInterval + 5
            saveLastFeed()
        
        #### Check if we are ready to feed
        if (time.time() - lastFeed) > feedInterval:
            printlcd(0,0, time.strftime("%m/%d %I:%M:%S%P", time.localtime(time.time())))
            printlcd(0,1, "Ready to feed   ")

            #### See if the button is pressed
            if buttonpressed(FEEDBUTTONPIN):
                lastFeed = feednow()
                saveLastFeed()
            
            #### Check if remote feed request is available
            elif remotefeedrequest():
                lastFeed = feednow()
                saveLastFeed()
                
        #### Since it is not time to feed yet, keep the countdown going
        else:
            timeToFeed = (lastFeed + feedInterval) - time.time()
            printlcd(0,0, time.strftime("%m/%d %I:%M:%S%P", time.localtime(time.time())))
            printlcd(0,1, 'Next:' + time.strftime("%Hh %Mm %Ss", time.gmtime(timeToFeed)))
            if buttonpressed(FEEDBUTTONPIN):
                lcd.clear()
                printlcd(0,0, "Not now, try at ")
                printlcd(0,1, time.strftime("%b/%d %H:%M", time.localtime(lastFeed + feedInterval)))
                time.sleep(2)
        time.sleep(.6)

#### Cleaning up at the end
except KeyboardInterrupt:
    logFile.close()
    lcd.clear()
    GPIO.cleanup()

except SystemExit:
    logFile.close()
    lcd.clear()
    GPIO.cleanup()
