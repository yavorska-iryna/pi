# pi

pupil dilation and ball tracking

pi_startup.py:

runs pi camera on raspberry pi

listens to TTL pulses to initiate and stop recording

saves timestamps of soundcard triggers

dependent on video_record.py and camera json file


pupil_dilation.py:

load .mp4 file and calculates PDR

saves output in .txt ( json format)

depending on your instalation of raspbian, extra dependencies that will need to be installed can vary: 
sudo apt-get install gpac #for mp4 conversion

sudo pip get install picamera numpy RPi json threading

you will also need:
sudo raspi-config
#to enable picamera and ssh 

to isntall opencv for pupil analysis: http://www.pyimagesearch.com/2015/07/27/installing-opencv-3-0-for-both-python-2-7-and-python-3-on-your-raspberry-pi-2/
