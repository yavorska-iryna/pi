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

depending on your instalation of raspian, extra dependencies that will need to be installed can vary: 
sudo apt-get install gpac %for mp4 conversion
sudo pip get install picamera numpy RPi json threading

you will also need:
sudo raspi-config
to enable picamera and ssh 
