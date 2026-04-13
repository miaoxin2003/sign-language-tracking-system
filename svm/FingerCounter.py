import cv2
import numpy as np
from HandTrackingModule import handDetector

detector = handDetector()
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break
    
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    
    fingers = []
    
    if len(lmList) != 0:
        fingers.append(1) if lmList[4][1] > lmList[3][1] else fingers.append(0)
        
        for id in range(1, 5):
            fingers.append(1) if lmList[id * 4 + 4][2] < lmList[id * 4 + 2][2] else fingers.append(0)
        
        cv2.putText(img, str(sum(fingers)), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 5)
    
    cv2.imshow("Image", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()