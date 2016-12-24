import cv2
import random as randint

cap = cv2.VideoCapture(0)
while (cap.isOpened()):
    #BGR image feed from camera
    ret,img = cap.read()

    ret, frame = cap.read()
    cv2.imshow('img1', frame)
    if cv2.waitKey(0) & 0xFF == ord('y'):
        cv2.imwrite('/CBSI/Test/Boaz/images/c87.png', frame)
        break
    break



cap.release()
cv2.destroyAllWindows()
