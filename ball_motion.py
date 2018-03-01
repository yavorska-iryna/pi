from inputs import devices
from threading import Timer
import numpy as np 
import RPi.GPIO as GPIO
import sys
import time
import json
from time import strftime

delay = .1 #change duty cycle every 100 ms
mouse = devices.mice[0]
GPIO.setmode(GPIO.BOARD)
channel = 15
GPIO.setup(channel, GPIO.OUT)

p = GPIO.PWM(channel,100)
p.start(50)
all_move_local = []


def baseline():
	p.ChangeDutyCycle(50)


def update_pin():
	if movements:
		move_local = movements
		global movements
                
		movements = []
		move_local = np.divide(move_local, 1.5)
		move_local = np.clip(move_local, -50, 50)
		move_local = move_local.mean(dtype=np.int)
		move_local +=50
		print(move_local)
		
		p.ChangeDutyCycle(100.0 - move_local)
		Timer(delay, update_pin).start()
	else:
		baseline()
		Timer(delay, update_pin).start()

movements = []
update_pin()
while 1:
	try:
		events=mouse.read()
		movements.extend([event.state for event in events if event.code == "REL_Y"])
	except KeyboardInterrupt:
		p.stop()
		GPIO.cleanup()
		time_string= strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
		name= "".join([time_string, '.txt'])
		with open(name, 'w') as f:
			json.dump(all_move_local, f, ensure_ascii=False)
