# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import cv2
import numpy as np
import serial


# Гауссовая фильтрация 20х20
# Размытие 5
# Точка стабилизации в центре
# ser = serial.Serial('COM3', 115200)

def get_median(cap, frame_num):
    frames = []
    for i in range(frame_num):
        ret, frame = cap.read()
        frame = frame[:, :, 2]
        frames.append(frame)
    # calculate the median
    median_frame = np.median(frames, axis=0).astype(np.uint8)
    return median_frame


vid = cv2.VideoCapture('C:/Users/Detsuya/Desktop/Test.mp4')
vid.set(cv2.CAP_PROP_POS_MSEC, 100000)
grayBase = get_median(vid, 10)
while vid.isOpened():
    # Video frame capturing
    # Display the resulting frame
    ret, frame = vid.read()
    frame = frame[:, :, 2]
    grayNew = cv2.GaussianBlur(frame, (51, 51), 5, cv2.BORDER_DEFAULT)
    # grayNew = cv.fastNlMeansDenoising(grayNew)
    # frame = cv.resize(frame, (640, 480), fx=0, fy=0, interpolation=cv.INTER_CUBIC)
    grayAbsDiff = cv2.absdiff(grayBase, grayNew)
    grayAbsDiv = np.divide(grayAbsDiff, grayBase)
    ret, thresh = cv2.threshold(grayAbsDiv, 0.12, 1, cv2.THRESH_BINARY)
    cv2.putText(grayAbsDiv, 'CV.AbsDiv', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
    cv2.putText(thresh, 'ThreshAbsDiffDiv', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)

    # grayNew = cv.resize(grayNew, (640, 480), interpolation=cv.INTER_AREA)
    grayAbsDiv = cv2.resize(grayAbsDiv, (800, 600), interpolation=cv2.INTER_AREA)
    thresh = cv2.resize(thresh, (800, 600), interpolation=cv2.INTER_AREA)
    output = np.hstack((grayAbsDiv, thresh))
    cv2.imshow('Difference', output)
    # cv.imshow('Original', grayNew)
    # the 'ESC' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('c'):
        grayBase = get_median(vid, 10)
    if cv2.waitKey(1) & 0xFF == 27:
        break
# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
