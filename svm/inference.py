import cv2
import joblib
import numpy as np
from HandTrackingModule import handDetector

model = joblib.load('gesture_model.pkl')

cap = cv2.VideoCapture(0)
detector = handDetector()

print("开始实时手势识别，按 'q' 退出")

while True:
    success, img = cap.read()
    if not success:
        break
        
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    
    if len(lmList) != 0:
        features = []
        for lm in lmList:
            features.extend([lm[1], lm[2]])
        
        prediction = model.predict([features])
        gesture = prediction[0]
        
        cv2.putText(img, f"Gesture: {gesture}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow("Image", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()