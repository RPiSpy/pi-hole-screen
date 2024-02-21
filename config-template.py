# Script Path
scriptPath = "/home/pi/pi-hole-screen"

# Place your Pi-Hole API Token within the double-quotes below
APItoken = "YOUR PIHOLE API TOKEN"

# Pi-Hole API End-point
APIsummaryURL="http://localhost/admin/api.php?summaryRaw"

# Define GPIO pins used by button and LED
ButtonGPIO=21
LEDGPIO=24

# Screen Mode
#  auto:   move onto the next mode after 30 seconds 
#  button: use connected button to trigger next mode
screenMode="auto"
