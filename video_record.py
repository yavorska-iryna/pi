import os
import json

import picamera

CONF_FILE = '/home/pi/pupil_dilation/camera_conf.json'

def load_conf(c_file):
    try:
        with open(c_file) as f:
            conf = json.load(f)
            f.close()

            #locals().update(conf)

    except:
        print('Couldnt load configuration')

    conf['resolution'] = (int(conf['width']),int(conf['height']))
    conf['framerate']  = int(conf['framerate'])
    conf['shutter_speed'] = int(conf['shutter_speed'])

    return conf

    

def init_camera(conf_file):
    conf = load_conf(conf_file)
    
    cam  = picamera.PiCamera()
    cam.resolution    = conf['resolution']
    cam.framerate     = conf['framerate']
    cam.shutter_speed = conf['shutter_speed']

    return cam



