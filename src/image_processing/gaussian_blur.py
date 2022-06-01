import cv2, sys
from matplotlib import pyplot as plt

img = cv2.imread("../images/output_ex.png")
grey_img = cv2.imread("../images/output_ex.png", cv2.IMREAD_GRAYSCALE)

# b, g, r = cv2.split(img)
# img2 = cv2.merge([r, g, b])
# plt.imshow(img2)
# plt.xticks([])
# plt.yticks([])
# plt.show()
# Box 형태의 kernel을 이미지에 적용한 후 평균값을 box의 중심점에 적용하는 형태
# kernel 크기 (3,3) 각 값은 홀수값으로 설정해야 한다.
# 크기가 커질 수록 더 흐릿해진다.
blur = cv2.GaussianBlur(grey_img, ksize=(3, 3), sigmaX=0)
# Thresholding은 바이너리 이미지를 만드는 가장 대표적인 방법.
# 바이너리 이미지란 검은색과 흰색만으로 표현되는 이미지.
# 여러 값을 어떤 임계점을 기준으로 두 가지 부류로 나누는 방법.
# 127보다 작으면 0, 127보다 크면 255
# ret = 바이너리 이미지에 사용된 Threshold 값.
# ret, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY)
# cv2.imshow(thresh)
# 10 = minVal = 다른 엣지와의 인접 부분 (엣지가 되기 쉬운 부분)의 엣지 여부를 판단하는 임계값.
# 작은 값으로 설정하면 이미 검출된 엣지를 길게 만든다.
# 250 = 엣지인지 아닌지 판단하는 임계값
# 작은 값으로 설정하면 엣지의 수가 많아진다.
edged = cv2.Canny(blur, 10, 250)

print("hi")
cv2.imshow("Edged", edged)
cv2.waitKey(0)
