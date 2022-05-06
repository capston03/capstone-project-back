import cv2
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt

# initialize segmentation model using mp.solutions.selfie_segmentation
change_background_mp = mp.solutions.selfie_segmentation
# select the segmentation function (selfie_segmentation)
change_bg_segment = change_background_mp.SelfieSegmentation()

# read image file and show it.
sample_img = cv2.imread('images/image4.jpeg')

# plt.figure(figsize=[10, 10])
#
# plt.title("Sample Image")
# plt.axis('off')
# plt.imshow(sample_img[:, :, ::-1])
# plt.show()

# BGR to RGB
RGB_sample_img = cv2.cvtColor(sample_img, cv2.COLOR_BGR2RGB)

# apply our selfie segmentation model to sample image.
result = change_bg_segment.process(RGB_sample_img)

# generate binary mask.
binary_mask = result.segmentation_mask > 0.8

binary_mask_3 = np.dstack((binary_mask, binary_mask, binary_mask))

output_image = np.where(binary_mask_3, sample_img, 255)

plt.figure(figsize=[22, 22])

plt.subplot(121)
plt.imshow(sample_img[:, :, ::-1])
plt.title("Original Image")
plt.axis('off')
plt.subplot(122)
plt.imshow(output_image[:, :, ::-1])
plt.title("Output Image")
plt.axis('off')
plt.show()
