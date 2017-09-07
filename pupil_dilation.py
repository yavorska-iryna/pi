# Inspired by https://www.learnopencv.com/object-tracking-using-opencv-cpp-python/

import json
import cv2
import sys
from skimage.morphology import label
import matplotlib.pyplot as plt
import numpy as np
from skimage.measure import regionprops
from skimage.exposure import adjust_sigmoid
import math
from tqdm import trange
import os
directory, video_file = sys.argv[1:]
#dir="C:\\Users\\lab\\Desktop"
os.chdir(directory) 
# Set parameters - these are particular to our setup, so experiment with your image to find the right ones.
CROP_Y = [0,480]
CROP_X = [0,1100]
THRESHOLD = 125
print('1')
#def pupil_dilation(dir,video_file):

# Basic preprocessing - cropping and contrast adjustment
def process_frame(frame, bbox):
    # crop frame (assuming CROP_X and Y are set in env)
    #frame = frame[CROP_Y[0]:CROP_Y[1], CROP_X[0]:CROP_X[1], :]
    frame = frame[bbox[1]:bbox[1]+bbox[2],bbox[0]:bbox[0]+bbox[3],:]
    # Adjust contrast
    frame = adjust_sigmoid(frame, gain=5, cutoff=0.1)
    return frame
    print('defined')

if __name__ == '__main__':
    print('main')
    # Set up tracker.
    # Instead of MIL, you can also use
    # BOOSTING, KCF, TLD, MEDIANFLOW or GOTURN
    tracker = cv2.TrackerKCF_create()

    # Open video
    video = cv2.VideoCapture(video_file)

    # Exit if video not opened.
    if not video.isOpened():
        print('Could not open video')
        sys.exit()

    # Total frames. Don't ask me about seven
    total_frames = int(video.get(7))

    # Read first frame.
    ok, frame = video.read()

    # Exit if can't get a frame
    if not ok:
        print('Cannot read video file')
        sys.exit()

    # Apply our preprocessing function
    #frame = process_frame(frame)

    # Select bounding box for object to track
    cv2.namedWindow("roi",cv2.WINDOW_NORMAL)
    crop_box = cv2.selectROI("roi", frame, False)
    cv2.destroyWindow("roi")

    print(crop_box)

    frame = process_frame(frame, crop_box)
    cv2.namedWindow("roi2",cv2.WINDOW_NORMAL)
    bbox = cv2.selectROI("roi2", frame, False)
    cv2.destroyWindow("roi2")


    # Initialize tracker with first frame and bounding box
    ok = tracker.init(frame, bbox)

    # Set up plotting
    fig, ax = plt.subplots()
    plt.ion()

    # We'll store pupil sizes in this list...
    pupil_size = []
    # trange makes a progress bar using tqdm
    for i in trange(total_frames):

        # Don't need to process every frame - empirically, every half-second seems to be entirely sufficient
        if i % 5 == 0:
            try:
                # Read a new frame
                ok, frame = video.read()
                if not ok:
                    break

                frame = process_frame(frame, crop_box)

                # Update tracker
                ok, bbox = tracker.update(frame)

                # Threshold image
                frame_g = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                ret,thresh = cv2.threshold(frame_g, THRESHOLD, 255, cv2.THRESH_BINARY_INV)

                # Find good region, set others to zero
                # Label segments into regions,
                # then we find which region is the most common within the bounding box

                thresh = label(thresh, background=0, connectivity=1)
                labels = np.reshape(thresh[int(bbox[1]):int(bbox[1]+bbox[3]),int(bbox[0]):int(bbox[0]+bbox[2])],-1)
                good_label = np.argmax(np.bincount(labels)[1:])+1
                thresh[thresh != good_label] = 0
                thresh[thresh == good_label] = 1

                # Just converts a boolean array to integers
                thresh = thresh + 0

                # Measures various properties about the region we found
                props = regionprops(thresh)
                prop = props[0] # should only be one

                y0, x0 = prop.centroid

                # This is the jankiest way of doing this, but it's acceptably fast.
                # Starting from the centroid, we travel along the major axis
                # until we reach the edge.
                edge = 0
                axis_length_1 = 10
                while edge == 0:
                    axis_length_1 += 1
                    x1 = int(np.round(x0 + math.cos(prop.orientation) * axis_length_1))
                    y1 = int(np.round(y0 - math.sin(prop.orientation) * axis_length_1))
                    if thresh[y1,x1] == 0:
                        edge = 1

                # Fit circle


                # Do the same thing for the other direction
                edge = 0
                axis_length_2 = 10
                while edge == 0:
                    axis_length_2 += 1
                    x2 = int(np.round(x0 - math.cos(prop.orientation) * axis_length_2))
                    y2 = int(np.round(y0 + math.sin(prop.orientation) * axis_length_2))
                    if thresh[y2,x2] == 0:
                        edge = 1

                # Add both together and append to your list
                #pupil_size.append((axis_length_1+axis_length_2))
                pupil_size.append(axis_length_1) 

            except:
            # If something goes wrong, don't break the whole thing,
            # just append zero and you can assume that it's an error rather than
            # the mouse's pupil collapsing into a singularity
                pupil_size.append(0)

            # Uncomment if you want to plot as you go
            ax.clear()
            ax.imshow(thresh)
            ax.plot((x0, x1), (y0, y1), '-r', linewidth=2.5)
            ax.plot(x0, y0, '.g', markersize=15)
            #ax.plot(pupil_size)
            plt.show()
            plt.pause(0.01)
            #p1 = (int(bbox[0]), int(bbox[1]))
            #p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            #cv2.rectangle(thresh, )



# At the end, plot and hold it up until closed
plt.figure()
plt.plot(pupil_size)
plt.show()
plt.show(block=True)
s=video_file[0:19]
name= ''.join(['pupil_',s,'.txt'])
with open(name, 'w') as f:
    json.dump(pupil_size, f, ensure_ascii=False)
        

    # You'll need to save these values obviously,
    # but since the form you want them in is going
    # to be so variable it's not really worth documenting here


