#! /usr/bin/env python

import sys
sys.path.append('/media/adafruitPyGit/Adafruit-Raspberry-Pi-Python-Code/Adafruit_MCP230xx')
sys.path.append('/media/adafruitPyGit/Adafruit-Raspberry-Pi-Python-Code/Adafruit_I2C')
import time 								#import system time
import os 									#add os library
import picamera 							#import the python camera controls
import smbus								#allows gpio on mcp23008 to communicate on i2c
import RPi.GPIO 		as GPIO 			#turn on gpio
from Adafruit_I2C		import Adafruit_I2C	#import Adafruit_I2C module
from Adafruit_MCP230xx 	import Adafruit_MCP230XX #import Adafruit_MCP230XX module
mcp = Adafruit_MCP230XX(busnum = 1, address = 0x20, num_gpios = 8) #define the i2c address and number of gpio

GPIO.setwarnings(False) 					## disables messages about GPIO pins already being in use
GPIO.setmode(GPIO.BOARD) 					## indicates which pin numbering configuration to use
GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #set pin to watch for the shutter button
GPIO.setup(35, GPIO.OUT) 					#set pin to send signal for image capture
GPIO.setup(35, GPIO.LOW) 					#set pin to OFF state 0/GPIO.LOW/False // pin for signal image capture
GPIO.setup(33, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  #set pin to watch for Saturation Switch
											#Add pin signifier that camera is on
											###### MCP23008 GPIO SETTINGS
mcp.pullup(0,1)								#set pin 1 to input with pullup resistor // Pin is attached to switch that grounds the pin to get an input signal
mcp.pullup(1,1) 							#set pin 2 to input with pullup resistor
mcp.pullup(2,1) 							#set pin 3 to input with pullup resistor
mcp.pullup(3,1) 							#set pin 4 to input with pullup resistor
mcp.pullup(4,1) 							#set pin 5 to input with pullup resistor

global imgCount 							#running image count variable
imgCount = 0

global saturationCount 						#variable to allow saturation adjustment
saturationCount = 0

global leftPress 							#variable to allow left arrow press
leftPress = 1

global cameraMenu
cameraMenu = 0

global cameraMenuISO
cameraMenuISO = 0


cameraSettings = {
	'ISO': 0, 								# 0 is auto, 100, 200, 400, 800, 1600
	'shutter_speed': 0, 					#0 is auto, otherwise is read as miliseconds
	'sharpness': 0, 						#0 to 100
	'contrast': 0,  						#0 to 100
	'brightness': 50, 						#0 to 100
	'saturation': 0,  						#-100 to 100
	'exposure_compensation': 0, 			#-25 to 25
	'exposure_mode': 'auto', 
	'meter_mode': 'average', 				#average, spot
	'awb_mode': 'auto',
	'image_effect': 'none',
	'color_effects': 'None'
}
cameraMenuTypes = 'ISO', 'Shutter Speed'
ISO = 0, 100, 200, 400, 800, 1600
ShutterSpeed = 0, 15, 10, 5, 1, 2.1, 4.1, 8.1, 15.1, 30.1, 60.1, 125.1, 250.1, 500.1 
ShutterSpeedMilli = 0, 15000, 10000, 5000, 1000, 500, 250, 125, 66.6, 33.3, 16.6, 8, 4, 2

def main():
	cameraReady() 							#start the infinite loop function

def cameraReady(): 							#idle loop keeping the program running while you do shit
	global imgCount 						#import global image count variable
	#print mcp.input(0)
	#print mcp.input(1)
	#print mcp.input(2)
	try: 									#create clean exit with a keyboard interupt hopefully control+c
   		while True: 						#infinite loop while waiting for button presses
			leftPress = (mcp.input(0))		#set pin 1 to be a left button
			rightPress = (mcp.input(1)>>1)	#set pin 2 to be a right button // >>1 shifts bits to make value = 1 or 0
			upPress = (mcp.input(2)>>2)		#set pin 3 to be an up button // >>2 shifts bits to make value = 1 or 0
			downPress = (mcp.input(3)>>3)	#set pin 4 to be an down button
			if leftPress != 1:				#The following if elif is a loop watching for a buttton press no interupt or event listener is included in the MCP_230XX module
				left()						#jump to def left()
				break						#break is needed to keep the "except KeyboardInterrupt" working
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
				time.sleep(.1) 				#sleep function to wait for button press
	except KeyboardInterrupt: 				#when you press control+c python throws a KeyboardInterupt, so do the GPIO cleanup
		GPIO.cleanup() 						#clean up GPIO

def saturationCallback(self): 				#Control saturation adjustment attached to push button currently
	global saturationCount 					#pull in global variable default starts at 0
	if saturationCount == 0:
		saturationCount = saturationCount + 1 #add 1 to saturationCount so we know the current state
		cameraSettings['saturation'] = -100 #change value for saturation key in cameraSettings Dict
		print "saturation is set to BW"
	else:
		saturationCount = 0 				#if saturation count already is 1, then this resets the count to 0
		cameraSettings['saturation'] = 0 	#make saturation normal again
		print "saturation is set to COLOR"
GPIO.add_event_detect(33, GPIO.RISING, callback=saturationCallback, bouncetime=300) #add listener for button press on saturation

def snapPmode(self):						#becuase this is a callback, it runs on a seperate thread than the main script
	global imgCount 						#import global count
	imgCount = imgCount + 1					#add 1 to the image count
	date_string = time.strftime("%H_%M_%S")	#create string with current time stamp
	GPIO.output(35,True) 					#turn on LED to signify start of image sequence
	with picamera.PiCamera() as camera: 	#start the camera image capture sequence

		########################
		##   CAMERA SETTINGS  ##
		########################
		#camera.start_preview() #start preview to adjust settings
		camera.resolution = (2592, 1944) #max resolution is (2592, 1944)
		camera.shutter_speed = cameraSettings['shutter_speed'] #value is miliseconds  <-------Pulled from camera settings dict
		camera.sharpness = cameraSettings['sharpness'] #0 to 100 <-------Pulled from camera settings dict
		camera.contrast = cameraSettings['contrast'] #0 to 100 <-------Pulled from camera settings dict
		camera.brightness = cameraSettings['brightness'] #0 to 100 <-------Pulled from camera settings dict
		camera.saturation = cameraSettings['saturation'] # -100 to 100 <-------Pulled from camera settings dict
		camera.ISO = cameraSettings['ISO'] # 0 is default auto but otherwise 100, 200, 400, 800, 1600 <-------Pulled from camera settings dict
		#camera.video_stabilization = False
		camera.exposure_compensation = cameraSettings['exposure_compensation'] # -25 to 25 <-------Pulled from camera settings dict
		camera.exposure_mode = cameraSettings['exposure_mode'] #<-------Pulled from camera settings dict
		camera.meter_mode = cameraSettings['meter_mode'] #spot, average <-------Pulled from camera settings dict
		camera.awb_mode = cameraSettings['awb_mode'] #<-------Pulled from camera settings dict
		camera.image_effect = cameraSettings['image_effect'] #<-------Pulled from camera settings dict
		#camera.color_effects = cameraSettings['color_effects'] #<-------Pulled from camera settings dict
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
		#########################
		## END CAMERA SETTINGS ##
		#########################
		
		time.sleep(.5)						#give the camera time to adjust the settings
		camera.capture('/media/piCam/foo_'+date_string+'_{0:04}.jpg'.format(imgCount)) #Capture image, add the date into the file name and add the global count variable into file name. Everytime the program turns off then back on the count resets.
		#camera.stop_preview() #stop preview
	GPIO.output(35,False) 					#Turn off LED to signify end of image capture sequence
GPIO.add_event_detect(37, GPIO.RISING, callback=snapPmode, bouncetime=300) #add listener for button press for shutter


def right():
	global cameraMenu 						#bring in global menu selector variable
	global cameraMenuISO 					#bring in global menu ISO variable
	if cameraMenu == 0: 					#Determines what menu item you're able to change
		cameraMenuISO = cameraMenuISO + 1 	#go to next menu item
		if cameraMenuISO > 5: 				#if you reach the last item available stop counting
			cameraMenuISO = 5 				#set to max variable
			cameraSettings['ISO'] = ISO[cameraMenuISO] #set the ISO setting to the cameraSettings Dict
			print cameraSettings['ISO'] 	#print the current setting for ISO listed from the Dict
		else:
			cameraSettings['ISO'] = ISO[cameraMenuISO] #set ISO setting to the list number associated with cameraMenuISO to Dict
			print cameraSettings['ISO'] 	#print the current setting for ISO listed from the Dict
	elif cameraMenu == 1:
		cameraMenuShutterSpeed == cameraMenuShutterSpeed + 1
		if cameraMenuShutterSpeed > 13:
			cameraMenuShutterSpeed = 13
			cameraSettings['shutter_speed'] = ShutterSpeedMilli[cameraMenuShutterSpeed]
			print ShutterSpeed[cameraMenuShutterSpeed]
		else:
			cameraSettings['shutter_speed'] = ShutterSpeedMilli[cameraMenuShutterSpeed]
			print ShutterSpeed[cameraMenuShutterSpeed]

	print "Right Button Pressed"
	time.sleep(.2)
	cameraReady()

def left():
	global cameraMenu
	global cameraMenuISO
	if cameraMenu == 0:
		cameraMenuISO = cameraMenuISO - 1
		if cameraMenuISO < 0:
			cameraMenuISO = 0
			cameraSettings['ISO'] = ISO[cameraMenuISO]
			print cameraSettings['ISO']
		else:
			cameraSettings['ISO'] = ISO[cameraMenuISO]
			print cameraSettings['ISO']
	elif cameraMenu == 1:
		cameraMenuShutterSpeed == cameraMenuShutterSpeed - 1
		if cameraMenuShutterSpeed < 0:
			cameraMenuShutterSpeed = 0
			cameraSettings['shutter_speed'] = ShutterSpeedMilli[cameraMenuShutterSpeed]
			print ShutterSpeed[cameraMenuShutterSpeed]
		else:
			cameraSettings['shutter_speed'] = ShutterSpeedMilli[cameraMenuShutterSpeed]
			print ShutterSpeed[cameraMenuShutterSpeed]

	print "Left Button Pressed"
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

def down():
	global cameraMenu
	cameraMenu = cameraMenu	+ 1
	if cameraMenu > 1:
		cameraMenu = 1
	print cameraMenuTypes[cameraMenu]
	time.sleep(.2)
	cameraReady()

cameraReady()								#lauch cameraReady def
GPIO.cleanup() 								#clean up the GPIO python pin library


#  ===============  #
#  [   S A M H   ]  #
#  ===============  #
