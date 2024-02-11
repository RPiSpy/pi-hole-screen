# pi-hole-screen
A repository for my 128x64 OLED screen add-on for Raspberry Pi based Pi-Hole systems.

# Current Status
This is a work in progress. The script is working but I need to update my blog post to explain how to implement it.

# Hardware Requirements
- A Raspberry Pi running Pi-Hole
- A 128x64 I2C OLED Screen
- (optional)LED with current limiting resistor connected to GPIOxx
- (optional)Momentary switch connected between GPIOxx and Ground

# Initial Setup
## Download project files
Use SSH to gain access to the Pi-Hole command line,
```
cd ~
```
Clone the project repository:
```
git clone https://github.com/RPiSpy/pi-hole-screen.git
```
Enter the new project folder:
```
cd pi-hole-screen
```
Rename the config-template.py file to config.py:
```
mv config-template.py config.py
```
Edit config.py and add your Pi-Hole API token:
```nano config.py```
Use CTRL-X, Y and ENTER to save and quit.

## Setup Python Virtual Environment
To ensure we don't interfere with the standard Python environment we will create a virtual environment to
run the script.
```
cd ~/pi-hole-screen
python3 -m venv venv
```
then activate it:
```
python venv/bin/activate
```
Then finally install the libraries required by the script:
```
python -m pip install requests
python -m pip install pillow
python -m pip install luma.oled
python -m pip install gpiozero
```

## Test the Script
In order to check the screen is working you can run the script:
```
python oled-screen.py
```
To quit the script use CTRL-C.

## Setup cron
Add a reference to crontab so the script launches when Pi-Hole reboots:
```
crontab -e
```
(If prompted select nano as the default editor)
Add the following line:
```
@reboot /home/pi/pi-hole-screen/venv/python /home/pi/pi-hole-screen/oled-screen.py >> /home/pi/Scripts/oled-screen.log 2>&1
```

## Reboot
Using the Pi-Hole web interface reboot the system via the "Settings" page.

## Troubleshooting
If the screen doesn't appear to work, get to the commandline and look at the contents of the oled-screen.log file.

# Fonts
The follow fonts are used by the script to display data on the screen:
- Big Shot by Portmanpreau - https://www.dafont.com/big-shot.font
- Pixel 12x10 by Corne2Plum3 - https://www.dafont.com/pixel12x10.font
- VCR OSD Mono by Riciery Leal - https://www.dafont.com/vcr-osd-mono.font
