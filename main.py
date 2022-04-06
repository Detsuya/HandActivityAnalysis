# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import cv2 as cv
import numpy as np
import serial


# ser = serial.Serial('COM3', 115200)
vid = cv.VideoCapture('C:/Users/Detsuya/Desktop/Hand5.avi')
vid.set(1, 700)
ret, frame = vid.read()
# frame = cv.resize(frame,(640,480),fx=0,fy=0, interpolation = cv.INTER_CUBIC)
grayBase = frame[:,:,2]

while vid.isOpened():
    # Video frame capturing
    # Display the resulting frame
    ret, frame = vid.read()
    grayNew = frame[:,:,2]
    # frame = cv.resize(frame, (640, 480), fx=0, fy=0, interpolation=cv.INTER_CUBIC)
    grayAbsDiff = cv.absdiff(grayBase, grayNew)
    grayAbsDiv = np.divide(grayAbsDiff, grayBase)
    ret, thresh1 = cv.threshold(grayAbsDiv, 0.2, 1, cv.THRESH_TOZERO)
    cv.putText(grayAbsDiv, 'CV.AbsDiv', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 2, 255)
    cv.putText(thresh1, 'ThreshAbsDiffDiv', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 2, 255)

    cv.imshow('Difference', thresh1)
    cv.imshow('Original', frame)
    # the 'ESC' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv.waitKey(1) & 0xFF == ord('c'):
        ret, frame = vid.read()
        grayBase = frame[:,:,2]

    if cv.waitKey(1) & 0xFF == 27:
        break
# After the loop release the cap object
vid.release()
# Destroy all the windows
cv.destroyAllWindows()
