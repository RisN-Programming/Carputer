# Andromeda
Carputer build for Seneca College

The system will interface with a vehicle to; display real-time vehicle parameters and current gear, provide a shift indicator light, provide audio playback features, as well as include user interface on a screen with 2 separate displays controllable by a toggle switch.

# Features
Although a single unit, the Carputer has 2 distinct sections, one being the car section and the other is the audio section. The car section interfaces with the car and performs related functions whereas the audio section acts as a media player and while it is used for audio playback in a vehicle it can be deployed as a standalone device

## Car section
The system will pull information from the vehicle’s ECU (engine control unit).

An LED based Shift indicator light. At configurable RPM values, 3 sections of 4 LEDs with various colors will turn on at separate RPMs and all LEDs will eventually flash when the rpm reaches the highest configured RPM to indicate it is time to shift. This is applicable to both manual transmissions as well as automatic transmissions equipped with manual shifting modes. In non-manual shifting automatics, or while in automatic mode, the LEDs will still be lit at the set RPM levels but gives no relevant information to the driver as the car will shift itself into gear.

A gear indicator using a 7seg display. Due to most cars not having an onboard gear value stored on the ECU, a calculation is done using speed and RPM values from the car to determine the current gear and it is then displayed on the 7seg display as the number 1-6. This is scalable as most manual transmission vehicles have 5-7 gears while some automatics can have 10+ gears.

GUI designed using Pygame to show current rpm, car speed, and gear on screen and when the GUI switch is flipped, the system will switch to another GUI specified in the audio section

## Audio section
The program will scan a specific folder for .mp3 files, the location will be configurable through changing the path within the .py file

Play .mp3 files using the OMXPlayer application present on the Raspberry PI

Output to either the car’s aux port to play audio through the internal speakers, or output to the HDMI display and use the built-in speakers.

2 buttons will be used for song control, one will be used to play next audio file in the folder while the other button will play the previous track. When at either end of the folder, the program will loop to the other end, i.e. pressing the next button while on the last song will loop back to the first song.

Volume adjustment, 2 buttons are used to increase or decrease volume, the volume when the program starts is set to 0.35 (or 35%), and by default the volume buttons will increase the audio volume by 5% and the volume will not go above 100% or below 0% 

GUI to display current volume and song title

The reason physical buttons are used as opposed to using a touch screen display is so that way, the driver’s eyes will not have to leave the road to see where on the screen they need to press in order to not miss and tap elsewhere on the screen.

# Operating Instructions

## Installation
The screen, LED’s and 7 seg display need to be placed within view of the driver. An ideal location involves; Being within the driver’s field of view so that the driver does not need to shift attention away from the road, not directly in the way of the windshield so as to not limit the driver’s vision, and not directly exposed to sunlight as it may push the Raspberry Pi past it’s temperature limit during high temperature days. To connect the Carputer to the car, the ELM327 module must be plugged into the OBDII port on the vehicle, usually located under the steering column on one of either side. The adapter’s red led will turn on when the vehicle is on to confirm the unit is receiving power. Next, power the raspberry pi by connected to a USB source, 2A recommended, this can be through a USB port present on the vehicle (read the owner's manual to see the current output of the port) or through the 12v port (commonly known as the cigarette lighter port) with an adapter to USB. 

## Startup and initialization
Through the Raspberry Pi OS or through terminal, pair the Pi to the ELM327 module. Place all music in the default folder (/home/pi/Music) or change the path to a more preferred location if desired. Once completed the python file may be started through terminal

## Once Deployed
The audio player starts with no music playing, press the previous or next button to start playing a track. Audio up and down buttons are used to increase or decrease volume (the default button delay is set to 900ms and can be adjusted to allow faster follow up presses but if adjusted to low may register multiple inputs when only 1 press was intended). Flip toggle switch to switch between car GUI and audio GUI. The escape key on a keyboard acts as a backup exit, it allows for a clean exit of the file by setting all components in an off state without turning the vehicle off. When the vehicle is turned off the Raspberry Pi will shut down with it unless the port from which it’s powered allows for current to be drawn while the vehicle is turned off.
