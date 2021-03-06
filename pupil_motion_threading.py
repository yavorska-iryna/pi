
import threading 

import RPi.GPIO as GPIO
import os
import sys
from time import gmtime, strftime, sleep
import video_record as vid
import time
import pickle
from datetime import datetime
import json

from inputs import devices
from threading import Timer
import numpy as np 
import time
from time import strftime


def baseline(i):
	p.ChangeDutyCycle(i)


def update_pin():
	global movements
	global all_movements
	if movements:
		move_local = movements
		movements = []
		move_local = np.divide(move_local, 1.5)
		move_local = np.clip(move_local, -50, 50)
		move_local = move_local.mean(dtype=np.int)
		move_local +=50
		
		all_movements.append(move_local)

		p.ChangeDutyCycle(100.0 - move_local)
		Timer(delay, update_pin).start()
	else:
		baseline(50)
		all_movements.append(50)
		Timer(delay, update_pin).start()

def run_ball_tracking():
	movements = []
	update_pin()
	while True:
		try:
			events=mouse.read()
			movements.extend([event.state for event in events if event.code == "REL_Y"])
		except KeyboardInterrupt:
			return




def start_listener(on_pin, off_pin, SCT_pin):
# Setup in for listening, set to be pulled down initially
    GPIO.setup(on_pin,  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(off_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(SCT_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Give the pin callbacks
    GPIO.add_event_detect(on_pin,  GPIO.RISING, bouncetime=200)
    GPIO.add_event_detect(off_pin, GPIO.RISING, bouncetime=200)
    GPIO.add_event_detect(SCT_pin, GPIO.RISING, bouncetime=100)

def run_pupil_tracking(on_pin, off_pin, SCT_pin):
    start_listener(on_pin, off_pin, SCT_pin)
    camera = vid.init_camera(vid.CONF_FILE)
    camera.crop=(.25, .25, .5, .5)
    camera.vflip= "True"
    camera.hflip= "True"
    camera.shutter_speed=6000
    camera.framerate=30
    # camera.contrast=80
    #camera.contrast=-15
    camera.iso = 1000
    #camera.brightness=70
    camera.exposure_compensation=25
    camera.exposure_mode='nightpreview'    

    print("Initialized camera")

    # Just chill and wait for some input
    while True:
        # Check every 1s if we've gotten a signal
        sleep(0.0001)
        
        if GPIO.event_detected(on_pin):
            time_string = strftime("%Y-%m-%d_%H-%M-%S",time.localtime())
            base_dir = '/home/pi/Videos'
            vfile = os.path.join(base_dir,"".join(['pupil_',time_string, '.h264']))
            print(vfile)
            camera.start_recording(vfile, format='h264')
            c=datetime.now()
            c=str(c)
            SCT=[]
            SCT.append(c)
            print("Started recording video to {}".format(vfile))
            camera.start_preview()

        if GPIO.event_detected(SCT_pin):
            c=datetime.now()
            c=str(c)
            SCT.append(c)

        if GPIO.event_detected(off_pin):
            camera.stop_recording()
            c=datetime.now()
            c=str(c)
            SCT.append(c)
            print("Stopped recording at {}".format(strftime("%H-%M-%S",time.localtime())))
            camera.stop_preview()
            vfile2=os.path.join(base_dir,"".join([time_string,'.mp4']))
            print(vfile)
            print(vfile2)
            #os.chdir('Videos')
            os.system(" MP4Box -add {} {} ".format(vfile,vfile2))
            os.system("rm {}".format(vfile)) 

            name=os.path.join(base_dir,"".join([time_string,'.txt']))
            print('Detected SCTs, saving in {}'.format(name))
            print(SCT)
            #os.chdir('Videos')   
            with open(name, 'w') as f:
                json.dump(SCT, f, ensure_ascii=False)
                print('saved SCTs in {}'.format(name))
            
            	SCT=[]


if __name__ == "__main__":

		# Set GPIO mode - determines how pins are numbered
	GPIO.setmode(GPIO.BOARD)

	#pi camera params
	on_pin  = 7
	off_pin = 11
	SCT_pin= 13
	SCT=[];


	# Base directory for recording, hardcoded for now
	base_dir = '/home/pi/Videos'

	#ball motion params

	delay = .1 #change duty cycle every 100 ms
	mouse = devices.mice[0]
	channel = 15
	GPIO.setup(channel, GPIO.OUT)
	p = GPIO.PWM(channel,100)
	p.start(50)
	all_move_local = []
	movements = []
	all_movements = []


	#Create Thread
	MotionThread = threading.Thread(target=run_ball_tracking, args=(all_movements)) 
	#Start Thread 
	MotionThread.start()

	#Create Thread
	PupilThread = threading.Thread(target=run_pupil_tracking, args=(on_pin, off_pin, SCT_pin)) 
	#Start Thread 
	PupilThread.start()

	MotionThread.join()
	PupilThread.join()


	GPIO.cleanup()
	time_string= strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
	name= "".join([time_string, '.txt'])
	with open(name, 'w') as f:
		json.dump(all_movements, f, ensure_ascii=False)
