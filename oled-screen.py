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
# A momentary button and an LED with current limiting resistor is optional.
#
# Author : Matt Hawkins
# Date   : 13/02/2024
# Source : https://github.com/RPiSpy/pi-hole-screen
#
# Additional details here:
# https://www.raspberrypi-spy.co.uk/2019/10/pi-hole-oled-status-screen/
#
# Written for Python 3.
#
# Python Libraries:
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
# python -m pip install pillow
# python -m pip install luma.oled
# python -m pip install gpiozero
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

# Import API token and Pi-Hole URLs
import config as c

# Function to handle button presses
def button_presssed():
  global mode
  if mode==2:
    mode=0
  elif mode==1:
    mode=2
  else:
    mode=1

# Configure button connected to GPIO21 (Pin 40) and Ground (Pin 39)
button = Button(c.ButtonGPIO)
button.when_pressed = button_presssed

# Configure LED connected to GPIO24 (Pin 18) and Ground (Pin 20)
led = PWMLED(c.LEDGPIO)
led.value=1

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

# Change to script directory
os.chdir(c.scriptPath)

# Load fonts
smlfont = ImageFont.truetype('fonts/big-shot.ttf',12)
medfont = ImageFont.truetype('fonts/Pixel12x10Mono-v1.1.0.ttf',16)
lrgfont = ImageFont.truetype('fonts/VCR_OSD_MONO_1.001.ttf',42)

# Default mode, show large percentage
mode=0

print("Enter main while loop. CTRL-C to quit.")

try:
  while True:

    try:
      # Get Pi-Hole data
      r1 = requests.get(c.APIsummaryURL+"&auth="+c.APItoken)
      # Pull out selected values into string variables
      v_ads_percent=str(round(r1.json()["ads_percentage_today"]))
      v_ads_blocked=str(r1.json()["ads_blocked_today"])
      v_status=str(r1.json()["status"])
      v_dns_queries=str(r1.json()["dns_queries_today"])
      v_clients_ever_seen=str(r1.json()["clients_ever_seen"])
      v_unique_clients=str(r1.json()["unique_clients"])
      led.value=1

    except:
      # Data failed, Use defaults.
      v_ads_percent="000"
      v_ads_blocked="000000"
      v_status="enabled"
      v_dns_queries="99999"
      v_clients_ever_seen="0"
      v_unique_clients="0"
      led.value=0

    # UNCOMMENT TO PRINT FULL SUMMARY OBJECT
    #print(json.dumps(r1.json(),indent=2))

    # UNCOMMENT TO USE TEST VALUES
    #v_ads_percent="100"
    #v_ads_blocked="999999"
    #v_status="disabled"
    #v_dns_queries="99999"
    #v_clients_ever_seen="999"
    #v_unique_clients="999"

    if v_status=="disabled":
      #Pi-Hole is disabled
      mode=5
      led.value=0
    elif mode==5:
      #Pi-Hole is not disabled but was previously
      mode=0
      led.value=1

    if mode==0:
      #
      # Large percentage with ads blocked today shown below
      #

      textLen=int(lrgfont.getlength(v_ads_percent+"%"))
      offset1=round((128-textLen)/2)
      textLen=int(medfont.getlength(v_ads_blocked))
      offset2=round((128-textLen)/2)

      # Scroll from right-hand side (x 128 to 0 in steps of 16)
      for x in range(128,-1,-8):

        with canvas(device) as draw:
          # Draw a black filled box to clear image.
          draw.rectangle(device.bounding_box, outline="black", fill="black")
          # Display large Pi-Hole ads blocked percentage
          draw.text((x+offset1, 0), v_ads_percent+"%",  font=lrgfont, fill=255)
          draw.text((x+offset2, 44), v_ads_blocked, font=medfont, fill=255)

        time.sleep(0.04)

      time.sleep(10)

      mode=1

    if mode==1:
      #
      # Get information about local system
      #   IP Address, CPU usage, Memory usage and Disk usage
      #

      # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
      cmd = "hostname -I | cut -d\' \' -f1"
      IP = subprocess.check_output(cmd, shell = True )

      # Write Pi-Hole data
      with canvas(device) as draw:
        draw.text((0, 0),  str(IP.decode('UTF-8')),   font=smlfont, fill=255)
        draw.text((0, 16), "B: %s%%" % v_ads_percent, font=smlfont, fill=255)
        draw.text((0, 32), "A: %s"   % v_ads_blocked, font=smlfont, fill=255)
        draw.text((0, 48), "Q: %s"   % v_dns_queries, font=smlfont, fill=255)

      time.sleep(5)

      mode=2

    if mode==2:
      #
      # Get information about local system
      #   IP Address, CPU usage, Memory usage and Disk usage
      #

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

      time.sleep(5)

      mode=0

    if mode==5:
      #
      # Pi-Hole is disabled
      #
      textLen=int(lrgfont.getlength("X"))
      offset=round((128-textLen)/2)
      with canvas(device) as draw:
        draw.text((offset, 0), "X", font=lrgfont, fill=255)
      time.sleep(10)


    time.sleep(10)

    # continue while loop

except KeyboardInterrupt:
  print("Aborted by user")
