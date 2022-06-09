from matplotlib import pyplot as plt
from PIL import Image, ImageEnhance
import cv2
import numpy as np
import skimage.exposure
from typing import Optional


class ImageUtility:
    # file -> matrix
    @staticmethod
    def conv_file_to_ndarray(path: str) -> np.ndarray:
        return cv2.imread(path)

    # file -> image
    @staticmethod
    def conv_file_to_pilimage(path: str) -> Image:
        return Image.open(path)

    # matrix -> image
    @staticmethod
    def conv_ndarray_to_pilimage(arr: np.ndarray) -> Image:
        return Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))

    # image -> matrix
    @staticmethod
    def conv_pilimage_to_ndarray(im: Image) -> np.ndarray:
        return np.array(im)

    # image -> cv2 matrix
    @staticmethod
    def conv_ndarray_to_cv2_image(arr: np.ndarray):
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    @staticmethod
    def conv_pilimage_to_cv2_image(im: Image):
        open_cv_image = np.array(im.convert('RGB'))
        # Convert RGB to BGR
        return open_cv_image[:, :, ::-1].copy()

        # resize image

    @staticmethod
    def resize(im: Image, ratio: float) -> Image:
        w = int(im.width * ratio)
        h = int(im.height * ratio)
        return im.resize((w, h))

    # remove black background
    @staticmethod
    def rm_black_bg(im):
        alpha = np.sum(im, axis=-1) > 0

        # Convert True/False to 0/255 and change type to "uint8" to match "na"
        alpha = np.uint8(alpha * 255)

        # Stack new alpha layer with existing image to go from BGR to BGRA, i.e. 3 channels to 4 channels
        res = np.dstack((im, alpha))
        return res

    @staticmethod
    def get_border_line(grey_img_cv2):
        # grey_img = cv2.imread("../images/output_ex.png", cv2.IMREAD_GRAYSCALE)
        # Box 형태의 kernel을 이미지에 적용한 후 평균값을 box의 중심점에 적용하는 형태
        # kernel 크기 (3,3) 각 값은 홀수값으로 설정해야 한다.
        # 크기가 커질 수록 더 흐릿해진다.
        blur = cv2.GaussianBlur(grey_img_cv2, ksize=(3, 3), sigmaX=0)
        # 10 = minVal = 다른 엣지와의 인접 부분 (엣지가 되기 쉬운 부분)의 엣지 여부를 판단하는 임계값.
        # 작은 값으로 설정하면 이미 검출된 엣지를 길게 만든다.
        # 250 = 엣지인지 아닌지 판단하는 임계값
        # 작은 값으로 설정하면 엣지의 수가 많아진다.
        return cv2.Canny(blur, 10, 200)

    @staticmethod
    def enhance_color(img_pil: Image) -> Image:
        # 색상 처리를 위한 Enhancer 지정
        change_color = ImageEnhance.Color(img_pil)

        # 색상 처리를 위한 값을 넣어준다.
        return change_color.enhance(2)


def grabcut(src_path: str, out_path: str,
            x_ratio, y_ratio, w_ratio, h_ratio):
    im = Image.open(src_path)
    im = ImageUtility.resize(im, 0.5)
    im_mtr = ImageUtility.conv_pilimage_to_cv2_image(im)
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
    rm_bg_result = ImageUtility.rm_black_bg(ImageUtility.conv_ndarray_to_cv2_image(grabcut_result))
    cv2.imwrite(out_path, cv2.cvtColor(rm_bg_result, cv2.COLOR_BGR2RGBA))
