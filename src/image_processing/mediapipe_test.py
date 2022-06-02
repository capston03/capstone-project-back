# DataFlair background removal
# import necessary packages
import os
import cv2
import numpy as np
import mediapipe as mp

selfie_segmentation = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)


def get_human(img_cv):
    rgb_img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    mask = selfie_segmentation.process(rgb_img_cv).segmentation_mask
    condition = np.stack((mask,) * 3, axis=-1) > 0.5
    result = np.where(condition, img_cv, 0)
    cv2.imshow("result", result)
    while True:
        key = cv2.waitKey(1)
        if key == ord('q'):
            break


img = cv2.imread("../data/human/obama.jpeg")
get_human(img)

# # initialize mediapipe
# mp_selfie_segmentation = mp.solutions.selfie_segmentation
# selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

# # create videocapture object to access the webcam
# cap = cv2.VideoCapture(0)
# while cap.isOpened():
#     _, frame = cap.read()
#     # flip the frame to horizontal direction
#     frame = cv2.flip(frame, 1)
#     height, width, channel = frame.shape
#
#     RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     # get the result
#     results = selfie_segmentation.process(RGB)
#     # extract segmented mask
#     mask = results.segmentation_mask
#     # show outputs
#     cv2.imshow("mask", mask)
#     cv2.imshow("Frame", frame)
#     key = cv2.waitKey(1)
#     if key == ord('q'):
#         break
#     # it returns true or false where the condition applies in the mask
#     condition = np.stack(
#         (results.segmentation_mask,) * 3, axis=-1) > 0.5
#     # resize the background image to the same size of the original frame
#     bg_image = cv2.resize(bg_image, (width, height))
#     # combine frame and background image using the condition
#     output_image = np.where(condition, frame, bg_image)
#     cv2.imshow("Output", output_image)
#     cv2.imshow("Frame", frame)
#     key = cv2.waitKey(1)
#     if key == ord('q'):
#         break
