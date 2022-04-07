# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import cv2 as cv
import numpy as np
import serial

#Гауссовая фильтрация 20х20
#Размытие 5
#Точка стабилизации в центре
# ser = serial.Serial('COM3', 115200)
vid = cv.VideoCapture('C:/Users/User/Desktop/Test.mp4')
vid.set(cv.CAP_PROP_POS_MSEC,100000)


ret, frame = vid.read()
grayBase = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
while vid.isOpened():
    # Video frame capturing
    # Display the resulting frame
    ret, frame = vid.read()
    frame = frame[:,:,2]
    grayNew = cv.GaussianBlur(frame, (21, 21), 5, cv.BORDER_DEFAULT)
    grayNew = cv.fastNlMeansDenoising(grayNew)
    # frame = cv.resize(frame, (640, 480), fx=0, fy=0, interpolation=cv.INTER_CUBIC)
    grayAbsDiff = cv.absdiff(grayBase, grayNew)
    grayAbsDiv = np.divide(grayAbsDiff, grayBase)
    ret, thresh = cv.threshold(grayAbsDiv, 0.15, 1, cv.THRESH_BINARY)
    cv.putText(grayAbsDiv, 'CV.AbsDiv', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 2, 255)
    cv.putText(thresh, 'ThreshAbsDiffDiv', (10, 50), cv.FONT_HERSHEY_SIMPLEX, 2, 255)

    #grayNew = cv.resize(grayNew, (640, 480), interpolation=cv.INTER_AREA)
    grayAbsDiv = cv.resize(grayAbsDiv, (800, 600), interpolation = cv.INTER_AREA)
    thresh = cv.resize(thresh,  (800, 600), interpolation=cv.INTER_AREA)
    output = np.hstack((grayAbsDiv, thresh))
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
