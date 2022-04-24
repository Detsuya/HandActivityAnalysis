# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import cv2
import numpy as np
import serial


# Гауссовая фильтрация 20х20
# Размытие 5
# Точка стабилизации в центре

def get_mean(cap, frame_num):
    frames = []
    for i in range(frame_num):
        ret, frame = cap.read()
        frame = frame[:, :, 2]
        frames.append(frame)
    # calculate the median
    mean_frame = np.mean(frames, axis=0).astype(np.uint8)
    return mean_frame


def show_video(frames, original=None):
    output = np.zeros((1000, 1), np.uint8)
    if len(frames) % 2:
        frames.append(0)
    new_weight = round(1920 / len(frames) * 2)
    new_height = round(1000 / 2)
    for i in range(0, len(frames), 2):
        output = np.concatenate((output, np.concatenate(
            (cv2.resize(frames[i], (new_weight, new_height), interpolation=cv2.INTER_AREA),
             cv2.resize(frames[i + 1], (new_weight, new_height), interpolation=cv2.INTER_AREA)), axis=0)),
                                axis=1)
    cv2.imshow('Difference', output)
    if original:
        cv2.imshow('Original', original)


vid = cv2.VideoCapture('C:/Users/Detsuya/Desktop/VideoTest/Test.mp4')
# vid.set(cv2.CAP_PROP_POS_MSEC, 100000)
grayBase = get_mean(vid, 5)
while vid.isOpened():
    ret, frame = vid.read()
    grayNew = frame[:, :, 2]
    # grayNew = cv2.GaussianBlur(frame, (51, 51), 5, cv2.BORDER_DEFAULT)
    # grayNew = cv.fastNlMeansDenoising(grayNew)
    # frame = cv.resize(frame, (640, 480), fx=0, fy=0, interpolation=cv.INTER_CUBIC)
    grayAbsDiff = cv2.absdiff(grayBase, grayNew)
    graySubtract = cv2.subtract(grayBase, grayNew)
    grayAbsDiv = np.divide(grayAbsDiff, grayBase)
    graySubDiv = np.divide(graySubtract, grayBase)
    cv2.putText(grayAbsDiv, 'AbsDiv', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
    cv2.putText(graySubDiv, 'SubDiv', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
    show_video([grayAbsDiff,grayAbsDiv,graySubtract,graySubDiv])
    if cv2.waitKey(1) & 0xFF == ord('c'):
        grayBase = get_mean(vid, 5)
    if cv2.waitKey(1) & 0xFF == 27:
        break
# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
