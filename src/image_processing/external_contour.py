import os
import cv2
import numpy as np

img = cv2.imread("../data/thumbnail/wordnumperiod-2022-06-03 01:10:17-9f263279-35e4-4fcf-ad2b-9f9fbb20b25c.png")
height = img.shape[0]
width = img.shape[1]
print(width, height)
col_range = [0.1788, 0.1788 + 0.3326]
col_range = [int(index * width) for index in col_range]
row_range = (0.3656, 0.3656 + 0.4996)
row_range = [int(index * height) for index in row_range]
img = img[row_range[0]:row_range[1], col_range[0]:col_range[1], ...]
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
canny = cv2.Canny(gray, 1, 800)
contours, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
for contour in contours:
    img = cv2.drawContours(img, [contour], -1, (0, 0, 255), 2)

cv2.imshow('img', img)
# cv2.imshow('gray', gray)

cv2.waitKey()
cv2.destroyAllWindows()
