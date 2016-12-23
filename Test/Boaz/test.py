import numpy
import cv2
import random as randint

cap = cv2.VideoCapture(0)
while (cap.isOpened()):
    #BGR image feed from camera
    ret,img = cap.read()

    ret, frame = cap.read()
    cv2.imshow('img1', frame)  # display the captured image
    if cv2.waitKey(0) & 0xFF == ord('y'):  # save on pressing 'y'
        cv2.imwrite('images/c'+str(randint(0, 1000000)) + '.png', frame)
        cv2.destroyAllWindows()
        break
    break



cap.release()
cv2.destroyAllWindows()
