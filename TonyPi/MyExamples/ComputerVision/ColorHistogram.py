# ColorHistogram.py
# This script demonstrates how to compute and display histograms for grayscale and color images.
# V1.0
#
# Tested on: 2024-01-03
#
import cv2
import numpy as np
import matplotlib
from matplotlib import pyplot as plt


plt.rcParams['image.cmap'] = 'gray'

# Check version of matplotlib, should be greter than or equal to 3.3.0.
print(matplotlib.__version__)

# Enable the test that you want to run.
TEST1 = False
TEST2 = False
TEST3 = False
TEST4 = False
TEST5 = False
TEST6 = False
TEST7 = False
TEST8 = False
TEST9 = False
TEST10 = True  # Color segmentation using HSV color space.

if TEST1:
    # Create a numpy array of 20x20x1 filled with zero values, equivalent to a black grayscale image.
    black_img = np.zeros([20, 20, 1])

    # Flatten the image data into a single 1D array.
    black_flatten = black_img.ravel()

    # Display the image and histogram.
    plt.figure(figsize=[18, 4])

    plt.subplot(131); plt.imshow(black_img); plt.title('Black Image')

    plt.subplot(132) 

    # create a histogram of this image using the default number of bins (10), 
    # and specify that the histogram should create these bins evenly across intensity values from 0 to 256. 
    # The upper end of this range is non inclusive, and so the histogram could ultimately show any pixel intensities 
    # up to and including a value of 255.
    plt.hist(black_flatten, range = [0, 256])
    plt.xlim([0, 256])
    plt.xlabel('Pixel Intensity')
    plt.ylabel('Numer of Pixels')
    plt.title('Histogram of black image')

if TEST2:
    # Read the image.
    img = cv2.imread('checkerboard_18x18.png', cv2.IMREAD_GRAYSCALE)

    # Flatten the image data into a single 1D array.
    try:
        img_flatten = img.ravel()
    except:
        print('Check the current directory contains the image file checkerboard_18x18.png.')

    # Display the image and histograms.
    plt.figure(figsize = [18, 4])

    plt.subplot(131); plt.imshow(img); plt.title('Original Image')

    plt.subplot(132) 
    plt.hist(img_flatten, 5, [0, 256])
    plt.xlim([0, 256])
    plt.xlabel('Pixel Intensity')
    plt.ylabel('Numer of Pixels')
    plt.title('5 Bins')

    plt.subplot(133)
    plt.hist(img_flatten, 50, [0, 256])
    plt.xlim([0, 256])
    plt.xlabel('Pixel Intensity')
    plt.ylabel('Numer of Pixels')
    plt.title('50 Bins')

if TEST3:
    # Read the image.
    img = cv2.imread('MNIST_3_18x18.png', cv2.IMREAD_GRAYSCALE)

    # Flatten the image data into a single 1D array.
    try:
        img_flatten = img.ravel()
    except:
        print('Check the current directory contains the image file MNIST_3_18x18.png.')

    # Display the image and histograms.
    plt.figure(figsize = [18, 4])

    plt.subplot(131); plt.imshow(img); plt.title('Original Image')
    plt.subplot(132); plt.hist(img_flatten, 5, [0, 256]);  plt.xlim([0, 256]); plt.title('5 Bins')
    plt.subplot(133); plt.hist(img_flatten, 50, [0, 256]); plt.xlim([0, 256]); plt.title('50 Bins')

if TEST4:
    # Read the image.
    img = cv2.imread('Apollo-8-Launch.jpg', cv2.IMREAD_GRAYSCALE)

    # Flatten the image data into a single 1D array.
    try:
        img_flatten = img.ravel()
    except:
        print('Check the current directory contains the image file Apollo-8-Launch.jpg.')

    # Display the image and histograms.
    plt.figure(figsize = [18, 4])
    plt.subplot(131); plt.imshow(img); plt.title('Original Image')
    plt.subplot(132); plt.hist(img_flatten, 50, [0,256]);  plt.xlim([0, 256]); plt.title('50 Bins')
    plt.subplot(133); plt.hist(img_flatten, 256, [0,256]); plt.xlim([0, 256]); plt.title('256 Bins')

if TEST5:
    # Read the image. cv2.IMREAD_GRAYSCALE est équivalent à 0
    img = cv2.imread('Apollo-8-Launch.jpg', 0)
    if img is None:
        print('Check the current directory contains the image file Apollo-8-Launch.jpg')
        exit(0)
    # Use calcHist() in OpenCV.
    # https://docs.opencv.org/3.4/d8/dbc/tutorial_histogram_calculation.html
    # parameters: 
    #   images
    #   channels : Graysacle img --> Only 1 channel --> channel = [0] (see link above for RGB images)
    #   mask, histSize
    hist = cv2.calcHist(images = [img], channels = [0], mask = None, histSize = [256], ranges = [0,255])

    # Flatten the image data.
    img_flatten = img.ravel()

    # Display the image and histograms.
    plt.figure(figsize = [18, 4])
    plt.subplot(131); plt.imshow(img); plt.title('Original Image')
    plt.subplot(132); plt.plot(hist); plt.xlim([0, 256]); plt.title('cv2.calcHist()')
    plt.subplot(133); plt.hist(img_flatten,256,[0,256]); plt.xlim([0, 256]); plt.title('np.ravel(), plt.hist()')

if TEST6:
    src = cv2.imread('Emerald_Lakes_New_Zealand.jpg')
    if src is None:
        print('Could not open or find the image: Emerald_Lakes_New_Zealand.jpg')
        exit(0)
    bgr_planes = cv2.split(src)
    histSize = 256
    histRange = (0, 256) # the upper boundary is exclusive
    accumulate = False
    b_hist = cv2.calcHist(bgr_planes, [0], None, [histSize], histRange, accumulate=accumulate)
    g_hist = cv2.calcHist(bgr_planes, [1], None, [histSize], histRange, accumulate=accumulate)
    r_hist = cv2.calcHist(bgr_planes, [2], None, [histSize], histRange, accumulate=accumulate)
    hist_w = 512
    hist_h = 400
    bin_w = int(round( hist_w/histSize ))
    histImage = np.zeros((hist_h, hist_w, 3), dtype=np.uint8)
    cv2.normalize(b_hist, b_hist, alpha=0, beta=hist_h, norm_type=cv2.NORM_MINMAX)
    cv2.normalize(g_hist, g_hist, alpha=0, beta=hist_h, norm_type=cv2.NORM_MINMAX)
    cv2.normalize(r_hist, r_hist, alpha=0, beta=hist_h, norm_type=cv2.NORM_MINMAX)
    for i in range(1, histSize):
        cv2.line(histImage, ( bin_w*(i-1), hist_h - int(b_hist[i-1]) ),
                ( bin_w*(i), hist_h - int(b_hist[i]) ),
                ( 255, 0, 0), thickness=2)
        cv2.line(histImage, ( bin_w*(i-1), hist_h - int(g_hist[i-1]) ),
                ( bin_w*(i), hist_h - int(g_hist[i]) ),
                ( 0, 255, 0), thickness=2)
        cv2.line(histImage, ( bin_w*(i-1), hist_h - int(r_hist[i-1]) ),
                ( bin_w*(i), hist_h - int(r_hist[i]) ),
                ( 0, 0, 255), thickness=2)
    cv2.imshow('Source image', src)
    cv2.imshow('calcHist Demo', histImage)
    cv2.waitKey()

if TEST7:
    # Read the color images.
    img = cv2.imread('Emerald_Lakes_New_Zealand.jpg')
    if img is None:
        print('Could not open or find the image: Emerald_Lakes_New_Zealand.jpg')
        exit(0)

    # Compute histograms for each color channel for both images.
    hist1 = cv2.calcHist([img], [0], None, [256], [0, 255])
    hist2 = cv2.calcHist([img], [1], None, [256], [0, 255])
    hist3 = cv2.calcHist([img], [2], None, [256], [0, 255])

    # Display the images and histogram plots.
    plt.figure(figsize = [18, 10])
    plt.subplot(221); plt.imshow(img[:, :, ::-1])

    plt.subplot(222) 
    plt.plot(hist1, 'b'); plt.plot(hist2, 'g'); plt.plot(hist3, 'r') 
    plt.xlim([0, 256])
    plt.ylim([0, 200000])

    # Using a mask with calcHist()

    # Create a mask to filter the image for the histogram calculation.
    # The mask is a binary image with the same dimensions as the original image but full of 0s.
    mask_hist = np.zeros((img.shape[0], img.shape[1]), dtype = 'uint8')

    # Select a region that isolates the green lake.
    # Update the mask to set the selected region to 255.
    mask_hist[2100:2400, 1500:2200] =  255

    # Create a similar mask to show the selected region in the image (for display purposes only).
    # The mask must have the same number of color channels as the image, but each color channel will
    # contain the same information.
    mat = [mask_hist, mask_hist, mask_hist]
    mask_3ch = cv2.merge(mat, 3)

    # Create an image that only shows the selected region of interest.
    # Apply mask_3ch to the original image using the bitwise_and() function.
    img_roi = cv2.bitwise_and(img, mask_3ch)

    # Compute histograms for each color channel for both images.
    hist1_lake = cv2.calcHist([img], [0], mask_hist, [256], [0, 255])
    hist2_lake = cv2.calcHist([img], [1], mask_hist, [256], [0, 255])
    hist3_lake = cv2.calcHist([img], [2], mask_hist, [256], [0, 255])

    # Display the images and histogram plots.
    #plt.figure(figsize = [18, 10])
    plt.subplot(223); plt.imshow(img_roi[:, :, ::-1])
    plt.subplot(224); plt.plot(hist1_lake, 'b'); plt.plot(hist2_lake, 'g'); plt.plot(hist3_lake, 'r') 
    plt.xlim([0, 256])
    plt.ylim([0, 10000])

if TEST8:
    print('Histogram Equalization is a non-linear method for enhancing contrast in an image.')
    # Read the image in grayscale format.
    img = cv2.imread('parrot.jpg', cv2.IMREAD_GRAYSCALE)
    if img is None:
        print('Could not open or find the image: parrot.jpg')
        exit(0)

    # Equalize histogram
    img_eq = cv2.equalizeHist(img)

    # Display the images.
    plt.figure(figsize = (18, 10))
    plt.subplot(221); plt.imshow(img); plt.title('Original Image')
    plt.subplot(222); plt.hist(img.ravel(), 256, [0, 256]); plt.title('Original Histogram')

    plt.subplot(223); plt.imshow(img_eq); plt.title('Equalized Image')
    plt.subplot(224); plt.hist(img_eq.ravel(), 256, [0, 256]); plt.title('Equalized Histogram')

if TEST9:

    # WRONG WAY TO PERFORM HISTOGRAM EQUALIZATION ON COLOR IMAGES
    # Read color image
    img = cv2.imread('parrot.jpg')
    if img is None:
        print('Could not open or find the image: parrot.jpg')
        exit(0)

    img_eq = np.zeros_like(img)

    # Peform histogram equalization on each channel separately.
    for i in range(0, 3):
        img_eq[:, :, i] = cv2.equalizeHist(img[:, :, i])

    # Compute histograms for each color channel for both images.
    hist1 = cv2.calcHist([img], [0], None, [256], [0, 255])
    hist2 = cv2.calcHist([img], [1], None, [256], [0, 255])
    hist3 = cv2.calcHist([img], [2], None, [256], [0, 255])
     
    hist1_eq = cv2.calcHist([img_eq], [0], None, [256], [0, 255])
    hist2_eq = cv2.calcHist([img_eq], [1], None, [256], [0, 255])
    hist3_eq = cv2.calcHist([img_eq], [2], None, [256], [0, 255])

    # Histogram equalization performed on the three channels separately leads to poor results
    plt.figure(figsize = (18, 8))

    plt.subplot(241); plt.imshow(img[:, :, ::-1]); plt.title('Original Color Image')
    plt.subplot(242); plt.plot(hist1, 'b'); plt.plot(hist2, 'g'); plt.plot(hist3, 'r')
    plt.subplot(243); plt.imshow(img_eq[:, :, ::-1]); plt.title('Equalized Image (wrong way)')
    plt.subplot(244); plt.plot(hist1_eq, 'b'); plt.plot(hist2_eq, 'g'); plt.plot(hist3_eq, 'r')

    plt.xlim([0, 256])
    plt.ylim([0, 200000])
    # CORRECT WAY TO PERFORM HISTOGRAM EQUALIZATION ON COLOR IMAGES
    # Read the color image.
    img = cv2.imread('parrot.jpg', cv2.IMREAD_COLOR)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)      # Convert to HSV.

    # Perform histogram equalization only on the V channel, for value intensity.
    img_hsv[:,:,2] = cv2.equalizeHist(img_hsv[:, :, 2])

    # Convert back to BGR format.
    img_eq_2 = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)
    hist1_eq = cv2.calcHist([img_eq_2], [0], None, [256], [0, 255])
    hist2_eq = cv2.calcHist([img_eq_2], [1], None, [256], [0, 255])
    hist3_eq = cv2.calcHist([img_eq_2], [2], None, [256], [0, 255])
    # Display the images.
    #plt.subplot(245); plt.imshow(img[:, :, ::-1]); plt.title('Original Color Image (right way)')
    plt.subplot(247); plt.imshow(img_eq_2[:, :, ::-1]); plt.title('Equalized Image (right way)')
    plt.subplot(248); plt.plot(hist1_eq, 'b'); plt.plot(hist2_eq, 'g'); plt.plot(hist3_eq, 'r')
    plt.tight_layout()

if TEST10:
    # Read the image in a 3 channel color format.
    #img = cv2.imread('opencv_logo.png', cv2.IMREAD_COLOR)
    img = cv2.imread('Emerald_Lakes_New_Zealand.jpg')
    if img is None:
        print('Could not open or find the image: Emerald_Lakes_New_Zealand.jpg')
        exit(0)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define Lower and Upper HSV Color Bounds
    # Set range for red color: array[H,S,V]
    # For the S and V components, we have selected a fixed range for all three colors to keep things simple
    r_lb = np.array([165, 50, 50], np.uint8)
    r_ub = np.array([180, 255, 255], np.uint8)

    # Set range for green color.
    g_lb = np.array([35, 50, 50], np.uint8)
    g_ub = np.array([80, 255, 255], np.uint8)

    # Set range for blue color.
    b_lb = np.array([95, 50, 50], np.uint8)
    b_ub = np.array([125, 255, 255], np.uint8)

    # Define a Color Mask for each Color
    r_mask = cv2.inRange(img_hsv, r_lb, r_ub)
    g_mask = cv2.inRange(img_hsv, g_lb, g_ub)
    b_mask = cv2.inRange(img_hsv, b_lb, b_ub)

    # Display each color mask.
    plt.figure(figsize = (18, 4))
    plt.subplot(141); plt.imshow(img[:, :, ::-1]); plt.title('Original Color Image')
    plt.subplot(142); plt.imshow(r_mask); plt.title('Red Mask')
    plt.subplot(143); plt.imshow(g_mask); plt.title('Green Mask')
    plt.subplot(144); plt.imshow(b_mask); plt.title('Blue Mask')


plt.show()  # Afficher l'histogramme (code saved in a .py file, running out of Jupyter notebook)