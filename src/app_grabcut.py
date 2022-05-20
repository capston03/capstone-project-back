from matplotlib import pyplot as plt
from PIL import Image
import cv2
import numpy as np
import skimage.exposure
from typing import Optional


def __conv_file_to_ndarray(path: str) -> np.ndarray:
    return cv2.imread(path)


def __conv_file_to_pilimage(path: str) -> Image:
    return Image.open(path)


def __conv_ndarray_to_pilimage(arr: np.ndarray) -> Image:
    return Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))


def __conv_pilimage_to_ndarray(im: Image) -> np.ndarray:
    return np.array(im)


def resize_im(im: Image, ratio: float) -> Image:
    w = int(im.width * ratio)
    h = int(im.height * ratio)
    return im.resize((w, h))


def crop(im: Image, margin: int) -> Image:
    ndarr_im = __conv_pilimage_to_ndarray(im)
    mask = ndarr_im != 255
    w = mask.shape[0]
    h = mask.shape[1]
    mask0, mask1 = mask.any(axis=0), mask.any(axis=1)
    col_start, col_end = mask0.argmax(), h - mask0[::-1].argmax()
    row_start, row_end = mask1.argmax(), w - mask1[::-1].argmax()
    return __conv_ndarray_to_pilimage(ndarr_im[max(0, row_start - margin):row_end + margin,
                                      max(0, col_start - margin):col_end + margin])


def grabcut(input_im: Image,
            x, y, w, h) -> Image:
    input_ndarr_im = __conv_pilimage_to_ndarray(input_im)
    copy = input_ndarr_im.copy()

    # Create the mask.
    mask = np.zeros(input_ndarr_im.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    start = (x, y)
    end = (x + w, y + h)
    rect = (x, y, w, h)
    cv2.rectangle(copy, start, end, (0, 0, 255), 3)

    # Apply the grabcut algorith.
    cv2.grabCut(input_ndarr_im, mask, rect, bgdModel, fgdModel, 100, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    rm_bg_im = input_ndarr_im * mask2[:, :, np.newaxis]
    rm_bg_pil_im = Image.fromarray(cv2.cvtColor(rm_bg_im, cv2.COLOR_BGR2RGB))
    return rm_bg_pil_im


input_im_path = "images/image7.jpeg"
output_im_path = "images/image7_output.jpeg"
input_im = Image.open(input_im_path)
resized_im = resize_im(input_im, 0.5)
rm_bg_im = grabcut(resized_im, 47, 78, 323, 246)
cropped_im = crop(rm_bg_im, 20)
cropped_im.save(output_im_path)

#
# # load image
# img = cv2.imread(output_im_path)
#
# # convert to gray
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
# # threshold
# thresh = cv2.threshold(gray, 11, 255, cv2.THRESH_BINARY)[1]
#
# # apply morphology to clean small spots
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
# morph = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, borderType=cv2.BORDER_CONSTANT, borderValue=0)
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
# morph = cv2.morphologyEx(morph, cv2.MORPH_CLOSE, kernel, borderType=cv2.BORDER_CONSTANT, borderValue=0)
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
# morph = cv2.morphologyEx(morph, cv2.MORPH_ERODE, kernel, borderType=cv2.BORDER_CONSTANT, borderValue=0)
#
# # get external contour
# contours = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# contours = contours[0] if len(contours) == 2 else contours[1]
# big_contour = max(contours, key=cv2.contourArea)
#
# # draw white filled contour on black background as mas
# contour = np.zeros_like(gray)
# cv2.drawContours(contour, [big_contour], 0, 255, -1)
#
# # blur dilate image
# blur = cv2.GaussianBlur(contour, (5, 5), sigmaX=0, sigmaY=0, borderType=cv2.BORDER_DEFAULT)
#
# # stretch so that 255 -> 255 and 127.5 -> 0
# mask = skimage.exposure.rescale_intensity(blur, in_range=(127.5, 255), out_range=(0, 255))
#
# # put mask into alpha channel of input
# result = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
# result[:, :, 3] = mask
#
# # save output
# cv2.imwrite('aerial_image_thresh.png', thresh)
# cv2.imwrite('aerial_image_morph.png', morph)
# cv2.imwrite('aerial_image_contour.png', contour)
# cv2.imwrite('aerial_image_mask.png', mask)
# cv2.imwrite('aerial_image_antialiased.png', result)
#
# # Display various images to see the steps
# # cv2.imshow('thresh', thresh)
# # cv2.imshow('morph', morph)
# # cv2.imshow('contour', contour)
# # cv2.imshow('mask', mask)
# # cv2.imshow('result', result)
# # cv2.imwrite("images/result.png", result)
#
# # cv2.waitKey(0)
# # cv2.destroyAllWindows()
