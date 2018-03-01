import cv2
import numpy as np
from matplotlib import pyplot as plt
from skimage import morphology, filters, restoration, segmentation

vid = cv2.VideoCapture('/home/jonny/test.mkv')

# get initial frame to find bounding box
ret, frame = vid.read()
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


roi = cv2.selectROI(frame)

def crop_image(image, roi):
    return image[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]

cropped_im = crop_image(frame, roi)

clahe = cv2.createCLAHE(clipLimit=3., tileGridSize=(10,10))
clahe_tf = clahe.apply(cropped_im)

params = cv2.SimpleBlobDetector_Params()
params.minThreshold = 0
params.maxThreshold = 256

params.filterByArea = True
params.minArea = 1000
params.filterByCircularity = True
params.minCircularity = 0.1
params.filterByConvexity = True
params.minConvexity = 0.5
params.filterByInertia = True
params.minInertiaRatio = 0.5

detector = cv2.SimpleBlobDetector_create(params)

cropped_im = cv2.equalizeHist(cropped_im)

plt.ion()

fig, ax = plt.subplots()
while True:
    ret, frame = vid.read()

    if ret == True:
        # Find edges
        #edges = cv2.Canny(frame, 50,50)
        #plt.imshow(edges)
        #plt.imshow(frame)

        # preprocessing
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = crop_image(frame, roi)

        frame = cv2.GaussianBlur(frame, (11, 11), 0)
        frame = morphology.erosion(frame)
        frame = morphology.erosion(frame)
        frame = morphology.erosion(frame)
        #frame = morphology.erosion(frame)
        #frame = morphology.erosion(frame)
        frame = filters.rank.enhance_contrast(frame, morphology.disk(5))

        #frame = clahe.apply(frame)
        frame = cv2.equalizeHist(frame)
        frame = cv2.GaussianBlur(frame, (11, 11), 0)

        #frame = cv2.GaussianBlur(frame, (11, 11), 0)

        #frame = cv2.GaussianBlur(frame, (11, 11), 0)

        #labels = np.zeros(frame.shape)
        #labels[200:300, 80:150] = 1

        #watersh = morphology.watershed(frame, labels, compactness=0)



        #thresh = cv2.adaptiveThreshold(frame, 100, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        #ret2, thresh = cv2.threshold(frame, 0, 100, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        edges = cv2.Canny(frame, 100, 100)
        #plt.imshow(np.hstack([frame,thresh]))
        #edges = cv2.Laplacian(frame, cv2.CV_64F, ksize=31)
        #edges = edges*(256./np.max(edges.flatten()))
        #edges = edges.astype("uint8")
        #edges = cv2.Canny(frame, 100, 200)

        #kpoints = detector.detect(frame)

        #im_w_kp = cv2.drawKeypoints(frame, kpoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        #im2, conts, hier  = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        #circles = cv2.HoughCircles(frame, method=cv2.HOUGH_GRADIENT, dp=1, minDist=500, param1=30, param2=50, minRadius=50, maxRadius = 300)

        # if circles is not None:
        #     circles = np.uint16(np.around(circles))
        #     for i in circles[0,:]:
        #         center = (i[0], i[1])
        #         cv2.circle(frame, center, 1, (0,100,100), 3)
        #         cv2.circle(frame, center, i[2], (255,0,255), 3)

        contours = segmentation.active_contour(frame, edges)


        ax.imshow(frame)
        ax.plot(contours[:,0], contours[:,1], '-r', lw=3)
        ax.axis([0, frame.shape[1], frame.shape[0], 0])

        #plt.imshow(np.hstack([frame]))
        #plt.imshow(watersh)


        #plt.imshow(im_w_kp)
        plt.pause(1)


        #ret2, thresh = cv2.threshold(frame, 0, 100, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        #plt.imshow(thresh)

    else:
        break

