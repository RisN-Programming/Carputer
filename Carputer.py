import os
import time
import RPi.GPIO as GPIO
import obd
import evdev
import glob
from omxplayer.player import OMXPlayer
from decimal import Decimal
import pygame
from pygame.locals import *
pygame.init()


#GPIO initialization
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#rpm GPIO
GPIO.setup(13,GPIO.OUT) #green
GPIO.setup(19,GPIO.OUT) #yellow
GPIO.setup(26,GPIO.OUT) #red

#7seg GPIO
GPIO.setup(12,GPIO.OUT) #e
GPIO.setup(16,GPIO.OUT) #d
GPIO.setup(18,GPIO.OUT) #b
GPIO.setup(20,GPIO.OUT) #c
GPIO.setup(23,GPIO.OUT) #a
GPIO.setup(24,GPIO.OUT) #f
GPIO.setup(25,GPIO.OUT) #g

#audio GPIO
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  #vol up
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  #vol down
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #previous
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #next

#ui switch GPIO
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#toggle switch

#constant OBDII data retrieval
connection = obd.Async(fast=False)

#//////////////////////////////////////////////////////////////
#variables

#audio variables
player = None
files = glob.glob('/home/pi/Music/*.mp3')#music location
file = 5
volume = 0.35
buttonDelay = .9
command = "sudo killall -s 9 omxplayer.bin"#end music player task

#OBDII variables
#initialize to 1 to avoid division by 0 exception
speed = 1
rpm = 1
g = 1
gear = 0
rpmLow = 2000   #rpm to turn on green leds
rpmMid = 2500   #rpm to turn on yellow leds
rpmHigh = 3000  #rpm to turn on red leds
rpmFlash = 3500 #rpm to flash all leds

#//////////////////////////////////////////////////////////////
#gui setup
screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
screen_w = screen.get_width()
screen_h = screen.get_height()

#set data location
upper_y = screen_h * .30
lower_y = screen_h * .85
rpm_x = screen_w * .10
speed_x = screen_w * .30
gear_x = screen_w * .50
vol_x = screen_w * .50
track_x = screen_w * .50

#set header location
rpmText_x = screen_w * .10
rpmText_y = screen_h * .10
speedText_x = screen_w * .30
speedText_y = screen_h * .10
gearText_x = screen_w * .50
gearText_y = screen_h * .10
volText_x = screen_w * .50
volText_y = screen_h * .20
trackText_x = screen_w * .50
trackText_y = screen_h * .75

#gui style
headerStyle = pygame.font.SysFont("Arial", 50)
digitStyle = pygame.font.SysFont("Arial", 50)
black = (0,0,0)
white = (255,255,255)

#//////////////////////////////////////////////////////////////
#gui design

def carHud():
    #background color
    screen.fill(black)
   
    #header design
    rpmText = headerStyle.render("RPM", True, white)
    speedText = headerStyle.render("Speed", True, white)    
    gearText = headerStyle.render("Gear", True, white)
   
    #header location
    rpmText_loc = rpmText.get_rect(center=(rpmText_x, rpmText_y))
    speedText_loc = speedText.get_rect(center=(speedText_x, speedText_y))  
    gearText_loc = gearText.get_rect(center=(gearText_x, gearText_y))

    #apply info
    screen.blit(rpmText, rpmText_loc)
    screen.blit(speedText, speedText_loc)
    screen.blit(gearText, gearText_loc)


def audioHud():
    #background color
    screen.fill(black)

    #header design
    volText = headerStyle.render("Volume", True, white)
    trackText = headerStyle.render("Track", True, white)

    #header location
    volText_loc = volText.get_rect(center=(volText_x, volText_y))
    trackText_loc = volText.get_rect(center=(trackText_x, trackText_y))

    #apply info
    screen.blit(volText, volText_loc)
    screen.blit(trackText, trackText_loc)

#//////////////////////////////////////////////////////////////  
#OBDII functions
def getRpm(r):
    global rpm
    rpm = int(r.value.magnitude)

def getSpeed(s):
    global speed
    speed = int(s.value.magnitude)

#//////////////////////////////////////////////////////////////
#audio functions

def playerExit(code):
    global playing
    playing=False

def playFile(file):
    global player,playing
    if player==None:
        player=OMXPlayer(file)
        player.set_volume(volume)
        player.exitEvent += lambda _, exit_code: playerExit(exit_code)
    else:
        os.system(command) #kill playing song before starting previous/next
        player.load(file)
    playing=True

#//////////////////////////////////////////////////////////////
#open connection to retrieve OBDII info

connection.watch(obd.commands.RPM, callback=getRpm)
connection.watch(obd.commands.SPEED, callback=getSpeed)
connection.start()



running = True
while running:
#exit using escape key
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False

#//////////////////////////////////////////////////////////////
#initialize and calculate volume to display

    output = Decimal(volume)
    output = output * 100
    output = round(output,0)

#//////////////////////////////////////////////////////////////
#gui display

    #car display
    if GPIO.input(4) == GPIO.HIGH:
        carHud()

        #convert information  
        rpmDisplay = digitStyle.render(str(rpm), 3, white)
        speedDisplay = digitStyle.render(str(speed), 3, white)
        gearDisplay = digitStyle.render((str(gear)), 3, white)
   
        #display information    
        screen.blit(rpmDisplay, (rpm_x, upper_y))
        screen.blit(speedDisplay,(speed_x, upper_y))
        screen.blit(gearDisplay, (gear_x, upper_y))
   
        pygame.display.update()

#audio display
    else:
        audioHud()

        #convert information  
        volDisplay = digitStyle.render(str(output) + "%", 3, white)
        trackDisplay = digitStyle.render((files[file][15:-4]), 3, white)

        screen.blit(volDisplay,volDisplay.get_rect(center=(vol_x, upper_y)))
        screen.blit(trackDisplay,trackDisplay.get_rect(center=(track_x, lower_y)))
   
        pygame.display.update()
   
#//////////////////////////////////////////////////////////////
#audio controls

#next track  
    if GPIO.input(27) == GPIO.HIGH:
        time.sleep(buttonDelay)
        file+=1
        if file>len(files)-1: #if at end of list, loop to beginning 
           file=0
        playFile(files[file])

#previous track  
    if GPIO.input(22) == GPIO.HIGH:
        time.sleep(buttonDelay)
        file-=1
        if file<0:            #if at beginning of list and previous pressed, loop to end 
           file=len(files)-1
        playFile(files[file])

#volume up
    if GPIO.input(5) == GPIO.HIGH:
        time.sleep(buttonDelay)
        volume+=0.05
        if volume>1:
           volume=1
        if player!=None: #only set volume once playing
           player.set_volume(volume)

#volume down
    if GPIO.input(6) == GPIO.HIGH:
        time.sleep(buttonDelay)
        volume-=0.05
        if volume<0:
           volume=0
        if player!=None: #only set volume once playing
           player.set_volume(volume)
         

#//////////////////////////////////////////////////////////////
#rpm indicator

#1 turn on green leds
    if (rpm > rpmLow and rpm < rpmFlash):
        GPIO.output(13,GPIO.HIGH)
    else:
        GPIO.output(13,GPIO.LOW)

#2 turn on yellow leds
    if (rpm > rpmMid and rpm < rpmFlash):
        GPIO.output(19,GPIO.HIGH)
    else:
        GPIO.output(19,GPIO.LOW)

#3 turn on red leds
    if (rpm > rpmHigh and rpm < rpmFlash):
        GPIO.output(26,GPIO.HIGH)
    else:
        GPIO.output(26,GPIO.LOW)

#4 flash all leds
    while (rpm > rpmFlash):
        GPIO.output(13,GPIO.HIGH)
        GPIO.output(19,GPIO.HIGH)
        GPIO.output(26,GPIO.HIGH)
        time.sleep(.1)

        GPIO.output(13,GPIO.LOW)
        GPIO.output(19,GPIO.LOW)
        GPIO.output(26,GPIO.LOW)
        time.sleep(.1)

#//////////////////////////////////////////////////////////////
#gear indicator
#1
    if(rpm>1000):
        g = speed/rpm
        
        if(g>0.006 and g<0.01):
            gear = 1
            GPIO.output(12,GPIO.LOW)
            GPIO.output(16,GPIO.LOW)
            GPIO.output(18,GPIO.HIGH)
            GPIO.output(20,GPIO.HIGH)
            GPIO.output(23,GPIO.LOW)
            GPIO.output(24,GPIO.LOW)
            GPIO.output(25,GPIO.LOW)
#2
        elif(g>0.011 and g<0.015):
            gear = 2
            GPIO.output(12,GPIO.HIGH)
            GPIO.output(16,GPIO.HIGH)
            GPIO.output(18,GPIO.HIGH)
            GPIO.output(20,GPIO.LOW)
            GPIO.output(23,GPIO.HIGH)
            GPIO.output(24,GPIO.LOW)
            GPIO.output(25,GPIO.HIGH)
#3
        elif(g>0.016 and g<0.02):
            gear = 3
            GPIO.output(12,GPIO.LOW)
            GPIO.output(16,GPIO.HIGH)
            GPIO.output(18,GPIO.HIGH)
            GPIO.output(20,GPIO.HIGH)
            GPIO.output(23,GPIO.HIGH)
            GPIO.output(24,GPIO.LOW)
            GPIO.output(25,GPIO.HIGH)
#4
        elif(g>0.022 and g<0.026):
            gear = 4
            GPIO.output(12,GPIO.LOW)
            GPIO.output(16,GPIO.LOW)
            GPIO.output(18,GPIO.HIGH)
            GPIO.output(20,GPIO.HIGH)
            GPIO.output(23,GPIO.LOW)
            GPIO.output(24,GPIO.HIGH)
            GPIO.output(25,GPIO.HIGH)
#5
        elif(g>0.027 and g<0.031):
            gear = 5
            GPIO.output(12,GPIO.LOW)
            GPIO.output(16,GPIO.HIGH)
            GPIO.output(18,GPIO.LOW)
            GPIO.output(20,GPIO.HIGH)
            GPIO.output(23,GPIO.HIGH)
            GPIO.output(24,GPIO.HIGH)
            GPIO.output(25,GPIO.HIGH)
#6
        elif(g>0.036 and g<0.04):
            gear = 6
            GPIO.output(12,GPIO.HIGH)
            GPIO.output(16,GPIO.HIGH)
            GPIO.output(18,GPIO.LOW)
            GPIO.output(20,GPIO.HIGH)
            GPIO.output(23,GPIO.HIGH)
            GPIO.output(24,GPIO.HIGH)
            GPIO.output(25,GPIO.HIGH)
#off       
        else:
            gear = 0
            GPIO.output(12,GPIO.LOW)
            GPIO.output(16,GPIO.LOW)
            GPIO.output(18,GPIO.LOW)
            GPIO.output(20,GPIO.LOW)
            GPIO.output(23,GPIO.LOW)
            GPIO.output(24,GPIO.LOW)
            GPIO.output(25,GPIO.LOW)

#neutral below 1k rpm display 0
    else:
        gear = 0
        GPIO.output(12,GPIO.HIGH)
        GPIO.output(16,GPIO.HIGH)
        GPIO.output(18,GPIO.HIGH)
        GPIO.output(20,GPIO.HIGH)
        GPIO.output(23,GPIO.HIGH)
        GPIO.output(24,GPIO.HIGH)
        GPIO.output(25,GPIO.LOW)

#//////////////////////////////////////////////////////////////
#on loop exit

#turn off rpm related gpio's
GPIO.output(13,GPIO.LOW)
GPIO.output(19,GPIO.LOW)
GPIO.output(26,GPIO.LOW)

#turn off gear indicator related gpio's      
GPIO.output(12,GPIO.LOW)
GPIO.output(16,GPIO.LOW)
GPIO.output(18,GPIO.LOW)
GPIO.output(20,GPIO.LOW)
GPIO.output(23,GPIO.LOW)
GPIO.output(24,GPIO.LOW)
GPIO.output(25,GPIO.LOW)

#turn off audio player
os.system(command)

#close connection to car
connection.stop()
connection.close()
