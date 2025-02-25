# Place your Pi-Hole API Token within the double-quotes below
APIpassword="YOUR PI-HOLE APP PASSWORD HERE"

# Script Path
scriptPath = "/home/pi/pi-hole-screen"

# Pi-Hole API End-points
APIauth="http://pi.hole/api/auth"
APIsummary="http://pi.hole/api/stats/summary"

# Define GPIO pins used by button and LED
ButtonGPIO=21
LEDGPIO=24

# Screen Mode
#  auto:   move onto the next mode after 30 seconds 
#  button: use connected button to trigger next mode
screenMode="auto"
