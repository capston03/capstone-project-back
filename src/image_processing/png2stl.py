from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from stl import mesh


def png2stl(src_im_path: str, out_stl_path: str):
    grey_im = Image.open(src_im_path).convert("L")
    max_size = (500, 500)
    max_height = 20
    min_height = 0

    # max_size 사이즈로 섬네일 제작.
    grey_im.thumbnail(max_size)
    # 읽은 이미지를 numpy 배열로 변환.
    im_mtr = np.array(grey_im)
    # 이미지 배열의 최소값, 최대값을 추출.
    max_pix = im_mtr.max()
    min_pix = im_mtr.min()
    # 이미지 배열의 행 수, 열 수 추출.
    ncols, nrows = grey_im.size
    # 각 이미지 배열의 원소마다 3개의 원소가 할당된다.
    vertices = np.zeros((nrows, ncols, 3))

    for x in range(0, ncols):
        for y in range(0, nrows):
            # 이미지 배열 안에 저장된 값은 pixel intensity이다.
            pixelIntensity = im_mtr[y][x]
            # pixel intensity값으로 해당 위치의 높이값을 계산한다.
            z = (pixelIntensity * max_height) / max_pix
            # 특정 위치의 높이값을 다음과 같이 설정한다.
            # 왜 y,x 가 x,y 로 바뀌었는가?
            vertices[y][x] = (x, y, z)

    faces = []

    # face를 다음과 같이 만든다.
    for x in range(0, ncols - 1):
        for y in range(0, nrows - 1):
            # create face 1
            vertice1 = vertices[y][x]
            vertice2 = vertices[y + 1][x]
            vertice3 = vertices[y + 1][x + 1]
            face1 = np.array([vertice1, vertice2, vertice3])

            # create face 2
            vertice1 = vertices[y][x]
            vertice2 = vertices[y][x + 1]
            vertice3 = vertices[y + 1][x + 1]

            face2 = np.array([vertice1, vertice2, vertice3])

            faces.append(face1)
            faces.append(face2)

    facesNp = np.array(faces)
    # Create the mesh
    surface = mesh.Mesh(np.zeros(facesNp.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            surface.vectors[i][j] = facesNp[i][j]
    # Write the mesh to file "cube.stl"
    surface.save(out_stl_path)


png2stl("images/aerial_image_antialiased.png", "stl/cup.stl")
