import cv2
import numpy as np
import mediapipe as mp
import skimage
from PIL import ImageEnhance
from PIL import Image

from image_processing.image_utility import ImageUtility


class BoundaryRecognizer:
    def __init__(self):
        self.__selfie_segmentation = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)

    def recognize_human(self, src_path: str, out_path: str):
        img = Image.open(src_path)
        img = self.__resize(img, 0.5)
        img_mtr = ImageUtility.conv_pilimage_to_ndarray(img)
        rgb_img_cv = cv2.cvtColor(img_mtr, cv2.COLOR_BGR2RGB)
        mask = self.__selfie_segmentation.process(rgb_img_cv).segmentation_mask
        condition = np.stack((mask,) * 3, axis=-1) > 0.5
        result = np.where(condition, img_mtr, 0)
        rm_bg_result = self.__rm_black_bg(result)
        cv2.imwrite(out_path, cv2.cvtColor(rm_bg_result, cv2.COLOR_BGR2RGBA))
        # cv2.imshow("result", result)
        # while True:
        #     key = cv2.waitKey(1)
        #     if key == ord('q'):
        #         break

    @staticmethod
    def __resize(im: Image, ratio: float) -> Image:
        w = int(im.width * ratio)
        h = int(im.height * ratio)
        return im.resize((w, h))

    # remove black background
    @staticmethod
    def __rm_black_bg(im):
        # # convert to gray
        # gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
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
        # result = cv2.cvtColor(im, cv2.COLOR_BGR2RGBA)
        # result[:, :, 3] = mask
        # Load image as Numpy array in BGR order
        # Make a True/False mask of pixels whose BGR values sum to more than zero
        alpha = np.sum(im, axis=-1) > 0

        # Convert True/False to 0/255 and change type to "uint8" to match "na"
        alpha = np.uint8(alpha * 255)

        # Stack new alpha layer with existing image to go from BGR to BGRA, i.e. 3 channels to 4 channels
        res = np.dstack((im, alpha))

        return res

    def recognize_object(self, src_path: str, out_path: str,
                         x_ratio, y_ratio, w_ratio, h_ratio):
        im = Image.open(src_path)
        im = BoundaryRecognizer.__resize(im, 0.5)
        im_mtr = ImageUtility.conv_pilimage_to_ndarray(im)
        copy = im_mtr.copy()

        # Create the mask.
        mask = np.zeros(im_mtr.shape[:2], np.uint8)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        x = int(x_ratio * im.width)
        w = int(w_ratio * im.width)
        y = int(y_ratio * im.height)
        h = int(h_ratio * im.height)
        start = (x, y)
        end = (x + w, y + h)
        rect = (x, y, w, h)
        cv2.rectangle(copy, start, end, (0, 0, 255), 3)

        # Apply the grabcut algorith.
        cv2.grabCut(im_mtr, mask, rect, bgd_model, fgd_model, 10, cv2.GC_INIT_WITH_RECT)
        bg_mask = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        grabcut_result = im_mtr * bg_mask[:, :, np.newaxis]
        rm_bg_result = self.__rm_black_bg(ImageUtility.conv_ndarray_to_cv2_image(grabcut_result))
        cv2.imwrite(out_path, cv2.cvtColor(rm_bg_result, cv2.COLOR_BGR2RGBA))
