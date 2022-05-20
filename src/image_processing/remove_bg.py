from typing import Tuple

import cv2
import numpy as np
from PIL import Image
import time


class BgRemover:
    def __init__(self, orig_path: str, resized_img_path: str, out_img_path: str):
        self.__orig_path = orig_path
        self.__resized_img_path = resized_img_path
        self.__out_img_path = out_img_path

    def __resize(self, ratio: float):
        img = Image.open(self.__orig_path)
        w = int(img.width * ratio)
        h = int(img.height * ratio)
        out = img.resize((w, h))
        out.save(self.__resized_img_path)

    def run(self, start_x: float, start_y: float, width: float, height: float):
        start_time = time.time()
        self.__resize(0.5)
        image = cv2.imread(self.__resized_img_path)
        copy = image.copy()

        # Create a mask (of zeros uint8 datatype) that is the same size (width, height) as our original image
        mask = np.zeros(image.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        start = (start_x, start_y)
        end = (start_x + width, start_y + height)
        rect = (start_x, start_y, width, height)
        cv2.rectangle(copy, start, end, (0, 0, 255), 3)

        # Apply the grabcut algorith.
        cv2.grabCut(image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        image = image * mask2[:, :, np.newaxis]
        im = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        im.save(self.__out_img_path)
        print("time :", time.time() - start_time)
