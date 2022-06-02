from matplotlib import pyplot as plt
from PIL import Image, ImageEnhance
import skimage.exposure
from typing import Optional
import cv2
import numpy as np
import mediapipe as mp


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
    def enhance_color(img_pil: Image) -> Image:
        # 색상 처리를 위한 Enhancer 지정
        change_color = ImageEnhance.Color(img_pil)

        # 색상 처리를 위한 값을 넣어준다.
        return change_color.enhance(2)

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
        return cv2.Canny(blur, 10, 250)
