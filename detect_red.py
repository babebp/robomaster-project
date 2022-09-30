import numpy as np
import cv2


def detect_red(image):
    cv2.imshow('original', image)
    result = image.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower1 = np.array([0, 100, 20])
    upper1 = np.array([10, 255, 255])

    lower2 = np.array([160,100,20])
    upper2 = np.array([179,255,255])

    lower_mask = cv2.inRange(image, lower1, upper1)
    upper_mask = cv2.inRange(image, lower2, upper2)

    mask = lower_mask + upper_mask
    result = cv2.bitwise_and(result, result, mask=mask)

    cv2.imshow('result', mask)
    cv2.waitKey()

img = cv2.imread('version_aow_jing.jpg')
detect_red(img)