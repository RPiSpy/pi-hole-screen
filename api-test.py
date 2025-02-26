#!/usr/bin/python3
#-----------------------------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
# Project : Pi-Hole Status Screen
# File    : summary-test.py
#
# Standalone script to test the Pi-Hole API. You must
# define the Pi-Hole App password. Run on the commandline
# and it will display query stats every 30 seconds.
#
# e.g.
# python3 summary-test.py
#
# Author : Matt Hawkins
# Date   : 25/02/2025
# Source : https://github.com/RPiSpy/pi-hole-screen
#
# Usage Details here:
# https://www.raspberrypi-spy.co.uk/2019/10/pi-hole-oled-status-screen/
#
# Written for Python 3.
#
# Local Pi-Hole API Documentation
# ===================================
# http://pi.hole/api/docs/
#
# JSON queries section returned by stats/summary endpoint
#
# queries: {
#   total              Total number of queries
#   blocked            Blocked queries
#   percent_blocked:   Percent of blocked queries
#   unique_domains:    Unique domains FTL knows
#   forwarded:         Queries that have been forwarded upstream
#   cached:            Queries replied to from cache or local config
#   frequency:         Average queries per second
# }

import requests
import json
import time

import config as c

# Main script
password={"password":c.APIpassword}

response= requests.post(c.APIauth,json=password)

if response.status_code==200:
  # Password was accepted
  print("New session created")
  data=response.json()

  SessionSID=data['session']['sid']
  SessionCSRF=data['session']['csrf']

  session={"sid":SessionSID,"csrf":SessionCSRF}

else:

  print("There was a problem creating a session")
  quit()


while True:

  # Use summary endpoint to get query stats
  response=requests.get(c.APIsummary,json=session)
  data=response.json()['queries']

  print("--------------------------")
  print("Total           : "+str(data['total']))
  print("Blocked         : "+str(data['blocked']))
  print("Percent Blocked : "+str(round(data['percent_blocked'],2))+"%")
  print("Unique Domains  : "+str(data['unique_domains']))
  print("Forwarded       : "+str(data['forwarded']))
  print("Cached          : "+str(data['cached']))
  print("Frequency       : "+str(round(data['frequency'],2)))

  time.sleep(30)
