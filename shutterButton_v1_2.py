#! /usr/bin/env python

import time #import system time
import os #add os library
import RPi.GPIO as GPIO #turn on gpio
import picamera #import the python camera controls
import sys
sys.path.append('/media/adafruitPyGit/Adafruit-Raspberry-Pi-Python-Code/Adafruit_MCP230xx')
sys.path.append('/media/adafruitPyGit/Adafruit-Raspberry-Pi-Python-Code/Adafruit_I2C')

from Adafruit_MCP230xx import Adafruit_MCP230xx 
mcp=Adafruit_MCP230xx(busnum=1, address=0x20, num_gpios=8)

GPIO.setwarnings(False) ## disables messages about GPIO pins already being in use
GPIO.setmode(GPIO.BOARD) ## indicates which pin numbering configuration to use

GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #set pin to watch for the shutter button
GPIO.setup(35, GPIO.OUT) #set pin to send signal for image capture
GPIO.setup(35, GPIO.LOW) #set pin to OFF state 0/GPIO.LOW/False // pin for signal image capture
GPIO.setup(33, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  #set pin to watch for Saturation Switch
#Add pin signifier that camera is on
###### MCP23008 GPIO SETTINGS
mcp.pullup(0,1)

global imgCount #running image count variable
imgCount = 0

global saturationCount #variable to allow saturation adjustment
saturationCount = 0

global leftPress #variable to allow left arrow press
leftPress = 1

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

cameraSettings = {
	'ISO': 0, # 0 is auto, 100, 200, 400, 800, 1600
	'shutter_speed': 0, #0 is auto, otherwise is read as miliseconds
	'sharpness': 0, #0 to 100
	'contrast': 0,  #0 to 100
	'brightness': 50, #0 to 100
	'saturation': 0,  #-100 to 100
	'exposure_compensation': 0, #-25 to 25
	'exposure_mode': 'auto', 
	'meter_mode': 'average', #average, spot
	'awb_mode': 'auto',
	'image_effect': 'none',
	'color_effects': 'None'
}


def cameraReady(): #idle loop keeping the program running while you do shit
	global imgCount #import global image count variable
	#with picamera.PiCamera() as camera:
	#PiCamera.start_preview() #start preview of camera
	try: #create clean exit with a keyboard interupt hopefully control+c
   		while True: #infinite loop while waiting for button presses
			leftPress = "%d" %(mcp.input(3) >> 3)
			if leftPress == 1:
				print "button pressed"
			time.sleep(.5) #sleep function to wait for button press
	except KeyboardInterrupt: #when you press control+c python throws a KeyboardInterupt, so do the GPIO cleanup
		GPIO.cleanup() #clean up GPIO

def saturationCallback(self): #Control saturation adjustment attached to push button currently
	global saturationCount #pull in global variable default starts at 0
	if saturationCount == 0:
		saturationCount = saturationCount + 1 #add 1 to saturationCount so we know the current state
		cameraSettings['saturation'] = -100 #change value for saturation key in cameraSettings Dict
		print "saturation is set to BW"
	else:
		saturationCount = 0 #if saturation count already is 1, then this resets the count to 0
		cameraSettings['saturation'] = 0 #make saturation normal again
		print "saturation is set to COLOR"


def snapPmode(self):
	global imgCount #import global count
	imgCount = imgCount + 1
	date_string = time.strftime("%H_%M_%S") #create string with current time stamp
	GPIO.output(35,True) #turn on LED to signify start of image sequence
	with picamera.PiCamera() as camera: #start the camera image capture sequence
		#camera.start_preview() #start preview to adjust settings
		#Default camera settings
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
		#END CAMERA SETTINGS
		time.sleep(.5)
		camera.capture('/media/piCam/foo_'+date_string+'_{0:04}.jpg'.format(imgCount)) #Capture image, add the date into the file name and add the global count variable into file name. Everytime the program turns off then back on the count resets.
		#camera.stop_preview() #stop preview
	GPIO.output(35,False) #Turn off LED to signify end of image capture sequence
	#cameraReady() #put camera back in ready state waiting for shutter button press

GPIO.add_event_detect(33, GPIO.RISING, callback=saturationCallback, bouncetime=300) #add listener for button press on saturation
GPIO.add_event_detect(37, GPIO.RISING, callback=snapPmode, bouncetime=300) #add listener for button press for shutter
cameraReady() #start the infinite loop function
GPIO.cleanup() #clean up the GPIO python pin library


#  ===============  #
#  [   S A M H   ]  #
#  ===============  #

