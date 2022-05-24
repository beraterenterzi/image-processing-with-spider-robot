import cv2
from imutils.video import VideoStream
import numpy as np
from collections import deque
import serial

# nesne merkezini depolayacak veri tipi
buffer_size = 16
pts = deque(maxlen=buffer_size)

# kirmizi renk aralığı HSV
redLower = (84, 98, 0)
redUpper = (179, 255, 255)

# capture
cap = cv2.VideoCapture(0)
cap.set(3, 960)
cap.set(4, 480)

while True:

    success, imgOriginal = cap.read()

    if success:

        # blur
        blurred = cv2.GaussianBlur(imgOriginal, (11, 11), 0)

        # hsv
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        cv2.imshow("HSV Image", hsv)

        # kirmizi için maske oluştur
        mask = cv2.inRange(hsv, redLower, redUpper)
        cv2.imshow("mask Image", mask)
        # maskenin etrafında kalan gürültüleri sil
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        cv2.imshow("Mask + erozyon ve genisleme", mask)

        # kontur
        (contours, _) = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        center = None

        if len(contours) > 0:

            # en buyuk konturu al
            c = max(contours, key=cv2.contourArea)

            # dikdörtgene çevir 
            rect = cv2.minAreaRect(c)

            ((x, y), (width, height), rotation) = rect

            s = "x: {}, y: {}, width: {}, height: {}, rotation: {}".format(np.round(x), np.round(y), np.round(width),
                                                                           np.round(height), np.round(rotation))
            print(s)

            # moment
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # arduino ile haberleşme ve yön komutları

            ser = serial.Serial('/dev/ttyUSB0', 9600)
            kamera = x, g = width

            if g < 150:

                ser.write(b'1')

            elif g < 300 and g >= 150:

                if (kamera < 200):
                    ser.write(b'2')

                elif (kamera <= 400 and kamera > 200):
                    ser.write(b'3')

                elif (kamera > 400):
                    ser.write(b'4')

            else:
                ser.write(b'5')
            # kutucuk
            box = cv2.boxPoints(rect)
            box = np.int64(box)

            # konturu çizdir: sarı
            cv2.drawContours(imgOriginal, [box], 0, (0, 255, 255), 2)

            # merkeze bir tane nokta çizelim: beyaz
            cv2.circle(imgOriginal, center, 5, (255, 255, 255), -1)

            # bilgileri ekrana yazdır
            cv2.putText(imgOriginal, s, (25, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 2)

            # b = "x: {}, y: {}".format(np.round( (int(M["m10"]/M["m00"]))),np.round(int(M["m01"]/M["m00"]))

        # deque
        pts.appendleft(center)

        for i in range(1, len(pts)):

            if pts[i - 1] is None or pts[i] is None: continue

            cv2.line(imgOriginal, pts[i - 1], pts[i], (0, 255, 0), 3)  #

        cv2.imshow("Orijinal Tespit", imgOriginal)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()

cv2.destroyAllWindows()
