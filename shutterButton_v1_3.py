#! /usr/bin/env python

import sys
sys.path.append('/media/adafruitPyGit/Adafruit-Raspberry-Pi-Python-Code/Adafruit_MCP230xx') #Path to the git repo that holds this file currently
sys.path.append('/media/adafruitPyGit/Adafruit-Raspberry-Pi-Python-Code/Adafruit_I2C')		#>>>>PUT IN THE URL OF GIT REPO HERE<<<<<
import time 										#import system time
import os 											#add os library
import picamera 									#import the python camera controls
import smbus										#allows gpio on mcp23008 to communicate on i2c
import RPi.GPIO 		as GPIO 					#turn on gpio
from Adafruit_I2C		import Adafruit_I2C			#import Adafruit_I2C module
from Adafruit_MCP230xx 	import Adafruit_MCP230XX 	#import Adafruit_MCP230XX module

#########################
## C H I P   S E T U P ##
#### M C P 2 3 0 0 8 ####
#########################

mcp = Adafruit_MCP230XX(busnum = 1, address = 0x20, num_gpios = 8) #define the i2c address and number of gpio


#########################
## G P I O   S E T U P ##
####### B O A R D #######
#########################

## G P I O   F O R   P I ##
GPIO.setwarnings(False) 							## disables messages about GPIO pins already being in use
GPIO.setmode(GPIO.BOARD) 							## indicates which pin numbering configuration to use
GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #set pin to watch for the shutter button
GPIO.setup(35, GPIO.OUT) 							#set pin to send signal for image capture
GPIO.setup(35, GPIO.LOW) 							#set pin to OFF state 0/GPIO.LOW/False // pin for signal image capture
													#Add pin signifier that camera is on

## M C P 2 3 0 0 8   G P I O ##
mcp.pullup(0,1)										#set pin 1 to input with pullup resistor // All Pins are attached to switch that grounds the pin to get an input signal
mcp.pullup(1,1) 									#set pin 2 to input with pullup resistor
mcp.pullup(2,1) 									#set pin 3 to input with pullup resistor
mcp.pullup(3,1) 									#set pin 4 to input with pullup resistor
mcp.pullup(4,1) 									#set pin 5 to input with pullup resistor


#######################
##### G L O B A L #####
## V A R I A B L E S ##
#######################

global imgCount 									#running image count variable
imgCount = 1

global cameraMenu 									#Variable picks the menu setting that the camera is on
cameraMenu = 0

global cameraMenuISO 								#for the ISO menu settings
cameraMenuISO = 0

global cameraMenuShutterSpeed 						#for the Shutter Speed menu settings
cameraMenuShutterSpeed = 0

global cameraMenuAWB 								#for the White Balance menu settings
cameraMenuAWB = 0

global cameraMenuMeter 								#for the Metering Mode menu settings
cameraMenuMeter = 0


#########################
###### C A M E R A ######
#### S E T T I N G S ####
## D I C T I O N A R Y ##
#########################

cameraSettings = {									#THESE SETTINGS LOAD AS THE DEFAULT BOOT SETTINGS FOR THE CAMERA
	'ISO': 0, 										# 0 is auto, 100, 200, 400, 800, 1600
	'shutter_speed': 0, 							#0 is auto, otherwise is read as microseconds
	'sharpness': 0, 								#0 to 100
	'contrast': 0,  								#0 to 100
	'brightness': 50, 								#0 to 100
	'saturation': 0,  								#-100 to 100
	'exposure_compensation': 0, 					#-25 to 25
	'exposure_mode': 'auto', 
	'meter_mode': 'average', 						#average, spot
	'awb_mode': 'auto',
	'image_effect': 'none',
	'color_effects': 'None'
}

#######################
####### M E N U  ######
##### B U T T O N #####
## V A R I A B L E S ##
#######################

##### CAMERA MENU OPTIONS FOR BUTTON CONTROL #####
cameraMenuTypes = 'ISO', 'Shutter Speed', 'White Balance', 'Meter Mode', 'Saturation', 'Contrast', 'Exposure Compensation'

##### VARIABLE LISTS FOR EACH MENU OPTION FOR BUTTON CONTROL #####
ISO = 0, 100, 200, 320, 400, 500, 640, 800
ShutterSpeed = 0, 30.1, 60.1, 125.1, 250.1, 500.1, 1000.1, 1500.1, 2000.1	#Have to use 2 variables here to display user friendly version on console
ShutterSpeedMicro = 0, 33333, 16666, 8000, 4000, 2000, 1000, 666, 500 		#and micoroseconds is necessary for PiCamera 
AWB = 'off', 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon'
Meter = 'average', 'spot'
Saturation = 0
Contrast = 0
ExposureComp = 0

###################
##### M A I N  ####
## P R O G R A M ##
###################

def mainStart():
	print "Hello World!"
	print "PiLaroid v1.3"
	#print "Dev: Garrett Martin"
	cameraReady() 									#start the infinite loop function

def cameraReady(): 									#idle loop keeping the program running while you do shit
	global imgCount 								#import global image count variable
	#print mcp.input(0)
	#print mcp.input(1)
	#print mcp.input(2)
	try: 											#create clean exit with a keyboard interupt hopefully control+c
   		while True: 								#infinite loop while waiting for button presses
			leftPress = (mcp.input(0))				#set pin 1 to be a left button
			rightPress = (mcp.input(1)>>1)			#set pin 2 to be a right button // >>1 shifts bits to make value = 1 or 0
			upPress = (mcp.input(2)>>2)				#set pin 3 to be an up button // >>2 shifts bits to make value = 1 or 0
			downPress = (mcp.input(3)>>3)			#set pin 4 to be an down button
			if leftPress != 1:						#The following if elif is a loop watching for a buttton press no interupt or event listener is included in the MCP_230XX module
				left()								#jump to def left()
				break								#break is needed to keep the "except KeyboardInterrupt" working
			elif rightPress != 1:
				right()
				break
			elif upPress != 1:
				up()
				break
			elif downPress != 1:
				down()
				break
			else:
				time.sleep(.1) 						#sleep function to wait for button press
	except KeyboardInterrupt: 						#when you press control+c python throws a KeyboardInterupt, so do the GPIO cleanup
		GPIO.cleanup() 								#clean up GPIO

def snapPmode(self):								#becuase this is a callback, it runs on a seperate thread than the main script
	global imgCount 								#import global count
	date_string = time.strftime("%H_%M_%S")			#create string with current time stamp
	GPIO.output(35,True) 							#turn on LED to signify start of image sequence
	with picamera.PiCamera() as camera: 			#start the camera image capture sequence


		##### C A M E R A   S E T T I N G S #####

		#camera.start_preview() 												#start preview to adjust settings
		camera.resolution = (2592, 1944) 										#max resolution is (2592, 1944)
		camera.shutter_speed = cameraSettings['shutter_speed'] 					#value is microseconds  <-------Pulled from camera settings dict
		camera.sharpness = cameraSettings['sharpness'] 							#0 to 100 <-------Pulled from camera settings dict
		camera.contrast = cameraSettings['contrast'] 							#0 to 100 <-------Pulled from camera settings dict
		camera.brightness = cameraSettings['brightness'] 						#0 to 100 <-------Pulled from camera settings dict
		camera.saturation = cameraSettings['saturation'] 						# -100 to 100 <-------Pulled from camera settings dict
		camera.ISO = cameraSettings['ISO'] 										# 0 is default auto but otherwise 100, 200, 400, 800, 1600 <-------Pulled from camera settings dict
		#camera.video_stabilization = False
		camera.exposure_compensation = cameraSettings['exposure_compensation'] 	# -25 to 25 <-------Pulled from camera settings dict
		camera.exposure_mode = cameraSettings['exposure_mode'] 					#<-------Pulled from camera settings dict
		camera.meter_mode = cameraSettings['meter_mode'] 						#spot, average <-------Pulled from camera settings dict
		camera.awb_mode = cameraSettings['awb_mode'] 							#<-------Pulled from camera settings dict
		camera.image_effect = cameraSettings['image_effect'] 					#<-------Pulled from camera settings dict
		#camera.color_effects = cameraSettings['color_effects'] 				#<-------Pulled from camera settings dict
		camera.rotation = 0
		camera.hflip = False
		camera.vflip = False
		#camera.crop = (0.0, 0.0, 1.0, 1.0)
		
		#Default camera settings
		#camera.sharpness = 0
		#camera.contrast = 0
		#camera.brightness = 50
		#camera.saturation = 0
		#camera.ISO = 0
		#camera.video_stabilization = False
		#camera.exposure_compensation = 0
		#camera.exposure_mode = 'auto'
		#camera.meter_mode = 'average'
		#camera.awb_mode = 'auto'
		#camera.image_effect = 'none'
		#camera.color_effects = None
		#camera.rotation = 0
		#camera.hflip = False
		#camera.vflip = False
		#camera.crop = (0.0, 0.0, 1.0, 1.0)

		##### E N D   C A M E R A   S E T T I N G S #####
		
		time.sleep(.5)								#give the camera time to adjust the settings
		camera.capture('/media/piCam/foo_'+date_string+'_{0:04}.jpg'.format(imgCount)) #Capture image, add the date into the file name and add the global count variable into file name. Everytime the program turns off then back on the count resets.
		#camera.stop_preview() #stop preview
	GPIO.output(35,False) 							#Turn off LED to signify end of image capture sequence
	imgCount = imgCount + 1							#add 1 to the image count
	print "I M A G E   C A P T U R E D"
GPIO.add_event_detect(37, GPIO.RISING, callback=snapPmode, bouncetime=1000) #add listener for button press for shutter


def right():
	global cameraMenu 								#bring in global menu selector variable
	global cameraMenuISO 							#bring in global menu ISO variable
	global cameraMenuShutterSpeed
	global cameraMenuAWB
	global cameraMenuMeter
	global Contrast

	##### I S O #####
	if cameraMenu == 0: 							#Determines what menu item you're able to change
		cameraMenuISO = cameraMenuISO + 1 			#go to next menu item
		if cameraMenuISO > len(ISO) - 1: 			#if you reach the last item available stop counting
			cameraMenuISO = len(ISO) - 1 			#set to max variable
			cameraSettings['ISO'] = ISO[cameraMenuISO] #set the ISO setting to the cameraSettings Dict
			print cameraMenuTypes[cameraMenu]
			print cameraSettings['ISO'] 			#print the current setting for ISO listed from the Dict
		else:
			cameraSettings['ISO'] = ISO[cameraMenuISO] #set ISO setting to the list number associated with cameraMenuISO to Dict
			print cameraMenuTypes[cameraMenu]
			print cameraSettings['ISO'] 			#print the current setting for ISO listed from the Dict
	
	##### S H U T T E R  S P E E D #####
	elif cameraMenu == 1:
		cameraMenuShutterSpeed = cameraMenuShutterSpeed + 1
		if cameraMenuShutterSpeed > len(ShutterSpeed) - 1:
			cameraMenuShutterSpeed = len(ShutterSpeed) - 1
			cameraSettings['shutter_speed'] = ShutterSpeedMicro[cameraMenuShutterSpeed]
			print cameraMenuTypes[cameraMenu]
			print ShutterSpeed[cameraMenuShutterSpeed]
		else:
			cameraSettings['shutter_speed'] = ShutterSpeedMicro[cameraMenuShutterSpeed]
			print cameraMenuTypes[cameraMenu]
			print ShutterSpeed[cameraMenuShutterSpeed]
	
	##### W H I T E  B A L A N C E #####
	elif cameraMenu == 2:
		cameraMenuAWB = cameraMenuAWB + 1
		if cameraMenuAWB > len(AWB) - 1:
			cameraMenuAWB = len(AWB) - 1
			cameraSettings['awb_mode'] = AWB[cameraMenuAWB]
			print cameraMenuTypes[cameraMenu]
			print cameraSettings['awb_mode']
		else:
			cameraSettings['awb_mode'] = AWB[cameraMenuAWB]
			print cameraMenuTypes[cameraMenu]
			print cameraSettings['awb_mode']

	##### M E T E R   M O D E #####
	elif cameraMenu == 3:
		cameraMenuMeter = cameraMenuMeter + 1
		if cameraMenuMeter > len(Meter) - 1:
			cameraMenuMeter = len(Meter) - 1
			cameraSettings['meter_mode'] = Meter[cameraMenuMeter]
			print cameraMenuTypes[cameraMenu]
			print cameraSettings['meter_mode']
		else:
			cameraSettings['meter_mode'] = Meter[cameraMenuMeter]
			print cameraMenuTypes[cameraMenu]
			print cameraSettings['meter_mode']
	
	##### S A T U R A T I O N #####
	elif cameraMenu == 4:
		Saturation = Saturation + 10
		if Saturation > 100:
			Saturation = 100
			cameraSettings['saturation'] = Saturation
			print cameraSettings['saturation']
		elif Saturation == 0:
			cameraSettings['saturation'] = Saturation
			print "Normal"
		elif Saturation < 0:
			cameraSettings['saturation'] = Saturation
			print "-", cameraSettings['saturation']
		else:
			cameraSettings['saturation'] = Saturation
			print "+", cameraSettings['saturation']

	##### C O N T R A S T #####
	elif cameraMenu == 5:
		Contrast = Contrast + 10
		if Contrast > 100:
			Contrast = 100
			cameraSettings['contrast'] = Contrast
			print "+", cameraSettings['contrast']
		elif Contrast == 0:
			cameraSettings['contrast'] = Contrast
			print "Normal"
		else:
			cameraSettings['contrast'] = Contrast
			print "+", cameraSettings['contrast']

	##### E X P O S U R E   C O M P E N S A T I O N #####
	elif cameraMenu == 6:
		ExposureComp = ExposureComp + 5
		if ExposureComp > 25:
			ExposureComp = 25
			cameraSettings['exposure_compensation'] = ExposureComp
			print cameraSettings['exposure_compensation']
		elif ExposureComp == 0:
			cameraSettings['exposure_compensation'] = ExposureComp
			print "Off"
		elif ExposureComp < 0:
			cameraSettings['exposure_compensation'] = ExposureComp
			print "-", cameraSettings['exposure_compensation']
		else:
			cameraSettings['exposure_compensation'] = ExposureComp
			print "+", cameraSettings['exposure_compensation']

	#print "Right Button Pressed"
	time.sleep(.2)
	cameraReady()

def left():
	global cameraMenu
	global cameraMenuISO
	global cameraMenuShutterSpeed
	global cameraMenuAWB
	global cameraMenuMeter
	global Contrast
	
	##### I S O #####
	if cameraMenu == 0:
		cameraMenuISO = cameraMenuISO - 1
		if cameraMenuISO < 0:
			cameraMenuISO = 0
			cameraSettings['ISO'] = ISO[cameraMenuISO]
			print cameraMenuTypes[cameraMenu]
			print cameraSettings['ISO']
		else:
			cameraSettings['ISO'] = ISO[cameraMenuISO]
			print cameraMenuTypes[cameraMenu]
			print cameraSettings['ISO']
	
	##### S H U T T E R  S P E E D #####
	elif cameraMenu == 1:
		cameraMenuShutterSpeed = cameraMenuShutterSpeed - 1
		if cameraMenuShutterSpeed < 0:
			cameraMenuShutterSpeed = 0
			cameraSettings['shutter_speed'] = ShutterSpeedMicro[cameraMenuShutterSpeed]
			print cameraMenuTypes[cameraMenu]
			print ShutterSpeed[cameraMenuShutterSpeed]
		else:
			cameraSettings['shutter_speed'] = ShutterSpeedMicro[cameraMenuShutterSpeed]
			print cameraMenuTypes[cameraMenu]
			print ShutterSpeed[cameraMenuShutterSpeed]
	
	##### W H I T E  B A L A N C E #####
	elif cameraMenu == 2:
		cameraMenuAWB = cameraMenuAWB - 1
		if cameraMenuAWB < 0:
			cameraMenuAWB = 0
			cameraSettings['awb_mode'] = AWB[cameraMenuAWB]
			print cameraMenuTypes[cameraMenu]
			print cameraSettings['awb_mode']
		else:
			cameraSettings['awb_mode'] = AWB[cameraMenuAWB]
			print cameraMenuTypes[cameraMenu]
			print cameraSettings['awb_mode']

	##### M E T E R   M O D E #####
	elif cameraMenu == 3:
		cameraMenuMeter = cameraMenuMeter - 1
		if cameraMenuMeter < 0:
			cameraMenuMeter = 0
			cameraSettings['meter_mode'] = Meter[cameraMenuMeter]
			print cameraMenuTypes[cameraMenu]
			print cameraSettings['meter_mode']
		else:
			cameraSettings['meter_mode'] = Meter[cameraMenuMeter]
			print cameraMenuTypes[cameraMenu]
			print cameraSettings['meter_mode']
	
	##### S A T U R A T I O N #####
	elif cameraMenu == 4:
		Saturation = Saturation - 10
		if Saturation < -100:
			Saturation = -100
			cameraSettings['saturation'] = Saturation
			print cameraSettings['saturation']
		elif Saturation == 0:
			cameraSettings['saturation'] = Saturation
			print "Normal"
		elif Saturation < 0:
			cameraSettings['saturation'] = Saturation
			print "-", cameraSettings['saturation']
		else:
			cameraSettings['saturation'] = Saturation
			print "+", cameraSettings['saturation']

	##### C O N T R A S T #####
	elif cameraMenu == 5:
		Contrast = Contrast - 10
		if Contrast < 0:
			Contrast = 0
			cameraSettings['contrast'] = Contrast
			print "Normal"
		else:
			cameraSettings['saturation'] = Contrast
			print "+", cameraSettings['contrast']

	##### E X P O S U R E   C O M P E N S A T I O N #####
	elif cameraMenu == 6:
		ExposureComp = ExposureComp - 5
		if ExposureComp < -25:
			ExposureComp = -25
			cameraSettings['exposure_compensation'] = ExposureComp
			print cameraSettings['exposure_compensation']
		elif ExposureComp == 0:
			cameraSettings['exposure_compensation'] = ExposureComp
			print "Normal"
		elif ExposureComp < 0:
			cameraSettings['exposure_compensation'] = ExposureComp
			print "-", cameraSettings['exposure_compensation']
		else:
			cameraSettings['exposure_compensation'] = ExposureComp
			print "+", cameraSettings['exposure_compensation']

	#print "Left Button Pressed"
	time.sleep(.2)
	cameraReady()

def up():
	global cameraMenu
	cameraMenu = cameraMenu	- 1
	if cameraMenu < 0:
		cameraMenu = 0
	print cameraMenuTypes[cameraMenu]
	time.sleep(.2)
	cameraReady()

def down():											# ONLY CHANGE SETINGS BELOW IF YOU ADD MORE MENU ITEMS
	global cameraMenu
	cameraMenu = cameraMenu	+ 1
	if cameraMenu > 5:								# ONLY CHANGE THIS COUNT IF YOU ADD MORE MENU ITEMS
		cameraMenu = 5								# ONLY CHANGE THIS COUNT IF YOU ADD MORE MENU ITEMS
	print cameraMenuTypes[cameraMenu]
	time.sleep(.2)
	cameraReady()

mainStart()											#lauch cameraReady def
GPIO.cleanup() 										#clean up the GPIO python pin library


#  ===============  #
#  [   S A M H   ]  #
#  ===============  #
