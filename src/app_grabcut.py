import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import time


# Show the image
def imshow(title="Image", image=None, size=10):
    w, h = image.shape[0], image.shape[1]
    aspect_ratio = w / h
    plt.figure(figsize=(size * aspect_ratio, size))
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title(title)
    plt.show()


def resize(input_path: str, output_path: str, ratio: float):
    img = Image.open(input_path)
    w = int(img.width * ratio)
    h = int(img.height * ratio)
    img_resize = img.resize((w, h))
    print(f"w: {w}, h:{h}")
    img_resize.save(output_path)


# Select the region of interest.

start_time = time.time()
origin_img = "images/image7.jpeg"
output_img = "images/image7_output.jpeg"
resize(origin_img, output_img, 0.5)

image = cv2.imread(output_img)
copy = image.copy()
# Create a mask (of zeros uint8 datatype) that is the same size (width, height) as our original image
mask = np.zeros(image.shape[:2], np.uint8)
bgdModel = np.zeros((1, 65), np.float64)
fgdModel = np.zeros((1, 65), np.float64)
# x, y, w, h = cv2.selectROI("select the area", image)
# start = (x, y)
# end = (x + w, y + h)
# rect = (x, y, w, h)
# print(x, y, w, h)
(x, y, w, h) = (47, 78, 323, 246)
start = (x, y)
end = (x + w, y + h)
rect = (x, y, w, h)
cv2.rectangle(copy, start, end, (0, 0, 255), 3)
# imshow("Input Image", copy)

# Apply the grabcut algorith.
cv2.grabCut(image, mask, rect, bgdModel, fgdModel, 100, cv2.GC_INIT_WITH_RECT)
mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
image = image * mask2[:, :, np.newaxis]
im = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
im.save("images/pixel_art_example.jpeg")
print("time :", time.time() - start_time)  # 현재시각 - 시작시간 = 실행 시간
# imshow("Mask", mask * 80)
# imshow("Mask2", mask2 * 255)
# imshow("Image", image)
