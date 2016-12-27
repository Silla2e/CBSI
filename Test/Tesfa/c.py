import cv2 
import numpy as np

image1 = cv2.imread("fb.jpg")
image2 = cv2.imread("watch.jpg")


cv2.imshow('img', image1)

difference = cv2.subtract(image1, image2)

result = not np.any(difference)#difference is zero

if result is True:
      print "the images are the same"
else:

    cv2.imwrite("difference.png", difference)

    print "the images are different"

