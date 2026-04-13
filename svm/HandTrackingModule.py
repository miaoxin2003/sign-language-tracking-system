import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import warnings
warnings.filterwarnings("ignore")
import cv2
import mediapipe as mp
import time
import serial
import joblib
import numpy as np


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.x_history = []
        self.y_history = []
        self.window_size = 5

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode,
                                        max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):

        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    if id == 4:
                        cv2.circle(img, (cx, cy), 15, (0, 0, 139), cv2.FILLED)
                    else:
                        cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

        return lmList


def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()

    ser = None
    try:
        ser = serial.Serial()
        ser.baudrate = 115200
        ser.port = 'COM10'
        ser.open()
        initial_data = '#'+str('320')+'$'+str('240')+'\r\n'
        ser.write(initial_data.encode())
    except serial.SerialException as e:
        ser = None

    try:
        model = joblib.load('gesture_model.pkl')
    except:
        model = None

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to capture image from camera.")
            break
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=True)
        
        if len(lmList) != 0 and model:
            features = []
            for lm in lmList:
                features.extend([lm[1], lm[2]])
            prediction = model.predict([features])
            cv2.putText(img, f"Gesture: {prediction[0]}", (400, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            thumb_tip_x = lmList[4][1]
            thumb_tip_y = lmList[4][2]
            
            detector.x_history.append(thumb_tip_x)
            detector.y_history.append(thumb_tip_y)
            if len(detector.x_history) > detector.window_size:
                detector.x_history.pop(0)
                detector.y_history.pop(0)
            
            if len(detector.x_history) > 3:
                avg_x = sum(detector.x_history) / len(detector.x_history)
                avg_y = sum(detector.y_history) / len(detector.y_history)
                if abs(thumb_tip_x - avg_x) > 50 or abs(thumb_tip_y - avg_y) > 50:
                    smooth_x = int(avg_x)
                    smooth_y = int(avg_y)
                else:
                    smooth_x = int(avg_x)
                    smooth_y = int(avg_y)
            else:
                smooth_x = thumb_tip_x
                smooth_y = thumb_tip_y
            
            if ser and ser.is_open:
                data = '#'+str(smooth_x)+'$'+str(smooth_y)+'\r\n'
                print(f"x: {smooth_x}  y: {smooth_y}")
                try:
                    ser.write(data.encode())
                except serial.SerialException as e:
                    print(f"Error writing to serial port: {e}")
                    ser.close()
                    ser = None

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == ord('s'):
            break

    if ser and ser.is_open:
        ser.close()
        print("Serial port closed.")
    cv2.destroyAllWindows()
    cap.release()


if __name__ == "__main__":
    main()