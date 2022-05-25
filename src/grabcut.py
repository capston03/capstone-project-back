from matplotlib import pyplot as plt
from PIL import Image
import cv2
import numpy as np
import skimage.exposure
from typing import Optional


# file -> matrix
def __conv_file_to_ndarray(path: str) -> np.ndarray:
    return cv2.imread(path)


# file -> image
def __conv_file_to_pilimage(path: str) -> Image:
    return Image.open(path)


# matrix -> image
def __conv_ndarray_to_pilimage(arr: np.ndarray) -> Image:
    return Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))


# image -> matrix
def __conv_pilimage_to_ndarray(im: Image) -> np.ndarray:
    return np.array(im)


def __conv_ndarray_to_cv2_image(arr: np.ndarray):
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


# resize image
def __resize_im(im: Image, ratio: float) -> Image:
    w = int(im.width * ratio)
    h = int(im.height * ratio)
    return im.resize((w, h))


# remove black background
def __rm_black_bg(im):
    # convert to gray
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    # threshold
    thresh = cv2.threshold(gray, 11, 255, cv2.THRESH_BINARY)[1]

    # apply morphology to clean small spots
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, borderType=cv2.BORDER_CONSTANT, borderValue=0)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    morph = cv2.morphologyEx(morph, cv2.MORPH_CLOSE, kernel, borderType=cv2.BORDER_CONSTANT, borderValue=0)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    morph = cv2.morphologyEx(morph, cv2.MORPH_ERODE, kernel, borderType=cv2.BORDER_CONSTANT, borderValue=0)

    # get external contour
    contours = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    big_contour = max(contours, key=cv2.contourArea)

    # draw white filled contour on black background as mas
    contour = np.zeros_like(gray)
    cv2.drawContours(contour, [big_contour], 0, 255, -1)

    # blur dilate image
    blur = cv2.GaussianBlur(contour, (5, 5), sigmaX=0, sigmaY=0, borderType=cv2.BORDER_DEFAULT)

    # stretch so that 255 -> 255 and 127.5 -> 0
    mask = skimage.exposure.rescale_intensity(blur, in_range=(127.5, 255), out_range=(0, 255))

    # put mask into alpha channel of input
    result = cv2.cvtColor(im, cv2.COLOR_BGR2RGBA)
    result[:, :, 3] = mask
    return result


def grabcut(src_im_path: str, out_im_path: str,
            x, y, w, h):
    im = Image.open(src_im_path)
    im = __resize_im(im, 0.5)
    ndarr_im = __conv_pilimage_to_ndarray(im)
    copy = ndarr_im.copy()

    # Create the mask.
    mask = np.zeros(ndarr_im.shape[:2], np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    start = (x, y)
    end = (x + w, y + h)
    rect = (x, y, w, h)
    cv2.rectangle(copy, start, end, (0, 0, 255), 3)

    # Apply the grabcut algorith.
    cv2.grabCut(ndarr_im, mask, rect, bgd_model, fgd_model, 10, cv2.GC_INIT_WITH_RECT)
    bg_mask = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    grabcut_result = ndarr_im * bg_mask[:, :, np.newaxis]
    rm_bg_result = __rm_black_bg(__conv_ndarray_to_cv2_image(grabcut_result))
    cv2.imwrite(out_im_path, cv2.cvtColor(rm_bg_result, cv2.COLOR_BGR2RGB))

# input_im_path = "images/image7.jpeg"
# output_im_path = "images/image7_output.jpeg"
# rm_bg_im = grabcut(resized_im, 47, 78, 323, 246)