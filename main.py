# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import cv2 as cv
import numpy as np
import serial

ser = serial.Serial('COM3', 115200)
vid = cv.VideoCapture(0)
ret, frame = vid.read()
grayBase = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
while vid.isOpened():
    # Video frame capturing
    # Display the resulting frame
    ret, frame = vid.read()
    grayNew = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    grayAbsDiff = cv.absdiff(grayBase, grayNew)
    grayAbsDiv = np.divide(grayAbsDiff, grayBase)
    graySub = cv.subtract(grayBase, grayNew)
    graySubDiv = np.divide(graySub, grayBase)
    ret, thresh1 = cv.threshold(grayAbsDiv, 0.15, 1, cv.THRESH_BINARY)
    ret, thresh2 = cv.threshold(graySubDiv, 0.15, 1, cv.THRESH_BINARY)

    cv.putText(grayAbsDiff, 'CV.AbsDiff', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 2, 0)
    cv.putText(grayAbsDiv, 'CV.AbsDiffDiv', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 2, 255)
    cv.putText(graySub, 'CV.Sub', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 2, 255)
    cv.putText(graySubDiv, 'CV.SubDiv', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 2, 255)
    cv.putText(thresh1, 'ThreshAbsDiffDiv', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 2, 0)
    cv.putText(thresh2, 'ThreshSubDiv', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 2, 0)

    output1 = np.vstack((grayAbsDiff, grayAbsDiv))
    output2 = np.vstack((graySub, graySubDiv))
    output3 = np.vstack((thresh1, thresh2))
    output = np.hstack((output1, output2, output3))
    cv.imshow('Difference', output)
    #cv.imshow('Original', grayNew)
    # the 'ESC' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv.waitKey(1) & 0xFF == ord('c'):
        ret, frame = vid.read()
        grayBase = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        ser.write('s'.encode("utf-8"))
        serAns = ser.read(3)
        print(serAns.decode("utf-8"))
    if cv.waitKey(1) & 0xFF == 27:
        break
# After the loop release the cap object
vid.release()
# Destroy all the windows
cv.destroyAllWindows()
