#!/usr/bin/python3
#-----------------------------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
# Project : Pi-Hole Status Screen
# File    : oled-screen.py
#
# Script to provide a status screen for a Pi-Hole system.
# Requires a 128x64 I2C OLED screen.
# A momentary button and an LED with current limiting resistor are optional.
#
# Author : Matt Hawkins
# Date   : 26/02/2025
# Source : https://github.com/RPiSpy/pi-hole-screen
#
# Usage Details here:
# https://www.raspberrypi-spy.co.uk/2019/10/pi-hole-oled-status-screen/
#
# Written for Python 3.
#
# Python Library Reference
# ===================================
# luma.oled library
# https://github.com/rm-hull/luma.oled
#
# gpiozero Button reference:
# https://gpiozero.readthedocs.io/en/stable/recipes.html#button
#
# gpiozero LED PWM reference:
# https://gpiozero.readthedocs.io/en/stable/recipes.html#led-with-variable-brightness
#
# Additional Python modules:
# ===================================
# python -m pip install requests
# python -m pip install luma.oled
# python -m pip install gpiozero
# python -m pip install lgpio
# python -m pip install pillow
# sudo apt install libopenjp2-7
#
# Fonts:
# ===================================
# Big Shot by Portmanpreau - https://www.dafont.com/big-shot.font
# Pixel 12x10 by Corne2Plum3 - https://www.dafont.com/pixel12x10.font
# VCR OSD Mono by Riciery Leal - https://www.dafont.com/vcr-osd-mono.font
#
#-----------------------------------------------------------

# Standard libraries
import os
import time
import json
import requests
import subprocess

# Graphics libraries
from PIL import ImageFont

# Import luma.oled library to drive screen
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

# GPIOZero functions for buttons and LEDs
from gpiozero import Button
from gpiozero import PWMLED

# Import API password and Pi-Hole URL from config.py
try:
  import config as c
except ModuleNotFoundError:
  print("Can't find config.py. Did you remember to rename config-template.py?")
  quit()

# Function to handle button presses
def button_presssed():
  global mode
  mode=mode+1
  if mode>2: mode=0

# Function to provide delay but
# quits if mode changes
def delayMe(currentMode,seconds):
  global mode
  counter=0
  while currentMode==mode and counter<seconds:
    counter=counter+1
    time.sleep(1)

# Configure button connected to GPIO21 (Pin 40) and Ground (Pin 39)
##button = Button(c.ButtonGPIO)
##button.when_pressed = button_presssed

# Configure LED connected to GPIO24 (Pin 18) and Ground (Pin 20)
#led = PWMLED(c.LEDGPIO)
##led.value=1

# Create connection to OLED screen at address 0x3C
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

# Change to script directory
os.chdir(c.scriptPath)

# Load fonts
smlfont = ImageFont.truetype('fonts/big-shot.ttf',12)
medfont = ImageFont.truetype('fonts/Pixel12x10Mono-v1.1.0.ttf',16)
lrgfont = ImageFont.truetype('fonts/VCR_OSD_MONO_1.001.ttf',42)

# Default mode, show large percentage number
mode=0

print("Enter main while loop. CTRL-C to quit.")

try:

  # Send password to get API session details
  password={"password":c.APIpassword}
  response= requests.post(c.APIauth,json=password)
  if response.status_code==200:
    print("New session created")
    data=response.json()
    SessionSID=data['session']['sid']
    SessionCSRF=data['session']['csrf']
    session={"sid":SessionSID,"csrf":SessionCSRF}
  else:
    print("There was a problem creating a session")
    quit()

  while True:

    try:
      # Get current status
      response=requests.get(c.APIblocking,json=session)
      v_status=response.json()['blocking']

      # Use summary endpoint to get query stats
      response=requests.get(c.APIsummary,json=session)
      data=response.json()['queries']

      # Pull out selected values into string variables
      v_total=str(data['total'])
      v_percent_blocked=str(round(data['percent_blocked']))
      v_blocked=str(data['blocked'])
      v_unique_domains=str(data['unique_domains'])
      v_forward=str(data['forwarded'])
      v_cached=str(data['cached'])
      v_frequency=str(round(data['frequency'],2))

      ##led.value=1

    except:
      # Data failed, Use defaults.
      v_total="000000"
      v_percent_blocked="000"
      v_blocked="000000"
      v_unique_domains="000000"
      v_forward="000000"
      v_cached="000000"
      v_frequency="000"

      ##led.value=0

    # UNCOMMENT TO USE TEST VALUES
    #v_total="999999"
    #v_percent_blocked="999"
    #v_blocked="999999"
    #v_unique_domains="999999"
    #v_forward="999999"
    #v_cached="999999"
    #v_frequency="999"

    if v_status=="disabled":
      #Pi-Hole is disabled
      mode=9
      ##led.value=0
    elif mode==9:
      #Pi-Hole is not disabled but was previously
      print("Re-enabled")
      mode=0
      ##led.value=1

    #
    # Large percentage with ads blocked today shown below
    #
    if mode==0:
      textLen=int(lrgfont.getlength(v_percent_blocked+"%"))
      offset1=round((128-textLen)/2)
      textLen=int(medfont.getlength(v_blocked))
      offset2=round((128-textLen)/2)

      # Scroll from left-hand side (x -128 to 0 in steps of 8)
      for x in range(-128,1,8):
        with canvas(device) as draw:
          # Draw a black filled box to clear image.
          draw.rectangle(device.bounding_box, outline="black", fill="black")
          # Display large Pi-Hole ads blocked percentage
          draw.text((x+offset1, 0), v_percent_blocked+"%",  font=lrgfont, fill=255)
          draw.text((x+offset2, 44), v_blocked, font=medfont, fill=255)

        time.sleep(0.04)

    #
    # Get information about local system
    #   IP Address, CPU usage, Memory usage and Disk usage
    #
    if mode==1:
      # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
      cmd = "hostname -I | cut -d\' \' -f1"
      IP = subprocess.check_output(cmd, shell = True )

      # Write Pi-Hole data
      with canvas(device) as draw:
        draw.text((0, 0),  str(IP.decode('UTF-8')),   font=smlfont, fill=255)
        draw.text((0, 16), "B: %s%%" % v_percent_blocked, font=smlfont, fill=255)
        draw.text((0, 32), "A: %s"   % v_blocked, font=smlfont, fill=255)
        draw.text((0, 48), "Q: %s"   % v_total, font=smlfont, fill=255)

    #
    # Get information about local system
    #   IP Address, CPU usage, Memory usage and Disk usage
    #
    if mode==2:
      # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
      cmd = "top -bn1 | grep load | awk '{printf \"C: %.2f\", $(NF-2)}'"
      CPU = subprocess.check_output(cmd, shell = True )
      cmd = "free -m | awk 'NR==2{printf \"M: %s/%sMB\", $3,$2 }'"
      MemUsage = subprocess.check_output(cmd, shell = True )
      cmd = "df -h | awk '$NF==\"/\"{printf \"D: %d/%dGB\", $3,$2}'"
      Disk = subprocess.check_output(cmd, shell = True )

      # Display system stats
      with canvas(device) as draw:
        draw.text((0, 0),  str(IP.decode('UTF-8')),       font=smlfont, fill=255)
        draw.text((0, 16), str(CPU.decode('UTF-8')),      font=smlfont, fill=255)
        draw.text((0, 32), str(MemUsage.decode('UTF-8')), font=smlfont, fill=255)
        draw.text((0, 48), str(Disk.decode('UTF-8')),     font=smlfont, fill=255)

    #
    # Pi-Hole is disabled
    #
    if mode==9:
      textLen=int(lrgfont.getlength("X"))
      offset=round((128-textLen)/2)
      with canvas(device) as draw:
        draw.text((offset, 0), "X", font=lrgfont, fill=255)


    # Wait for 30 seconds or until mode changes
    delayMe(mode,30)

    # if screenMode is auto then move to the next mode
    if c.screenMode=="auto":
      mode=mode+1
      if mode>2: mode=0

    # continue while loop

except KeyboardInterrupt:
  print("Aborted by user")
