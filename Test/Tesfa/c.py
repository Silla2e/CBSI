import cv2 
import numpy as np

image1 = cv2.imread("ph_0.png")
image2 = cv2.imread("ph_1.png")

difference = cv2.subtract(image1, image2)

result = not np.any(difference)#difference is zero

if result is True:
      print "the images are the same"
else:

    cv2.imwrite("difference.png", difference)

    print "the images are different"

