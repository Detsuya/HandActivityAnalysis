import cv2
import vapoursynth as vs
from vapoursynth import core
import numpy as np
import time
import scipy
from scipy import ndimage


def show_video(frames, original=None):
    if len(frames) > 1:
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
    else:
        output = frames[0]
    cv2.imshow('Difference', output)
    if original.any():
        cv2.imshow('Original', original)


def get_mean(cap, frame_num):
    frames = []
    global frame_ptr
    for i in range(frame_num):
        frame = cap.get_frame(frame_ptr)
        frame_ptr += 1
        frame = np.asarray(frame[0])
        frames.append(frame)
    # calculate the mean
    mean_frame = np.mean(frames, axis=0).astype(np.single)
    return mean_frame


video = core.ffms2.Source(source='C:/Users/Detsuya/Desktop/VideoTest/3.mp4', format=vs.RGBS, width=1920, height=1080)
frame_ptr = 0
base_frame = get_mean(video, 1)
while (True):
    frame = video.get_frame(frame_ptr)
    frame_ptr += 1
    original_frame = np.asarray(frame[0])
    curr_frame = scipy.ndimage.gaussian_filter(original_frame, 5, truncate=4)
    curr_frame = cv2.absdiff(base_frame, curr_frame)
    curr_frame = np.divide(curr_frame, base_frame)
    cap, curr_frame2 = cv2.threshold(curr_frame, 0.1, 1, cv2.THRESH_BINARY)
    show_video([curr_frame], original_frame)
    # time.sleep(0.1)
    if cv2.waitKey(1) & 0xFF == ord('c'):
        base_frame = get_mean(video, 1)
    if cv2.waitKey(1) & 0xFF == 27:
        break
cv2.destroyAllWindows()
