from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from stl import mesh


# Do not use. (Deprecated)
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
    # min_pix = im_mtr.min()
    # 이미지 배열의 행 수, 열 수 추출.
    ncols, nrows = grey_im.size
    # 각 이미지 배열의 원소마다 3개의 원소가 할당된다.
    vertices = np.zeros((nrows, ncols, 3))

    vertices = np.fromfunction()
    for x in range(0, ncols):
        for y in range(0, nrows):
            # 이미지 배열 안에 저장된 값은 pixel intensity이다.
            pixel_intensity = im_mtr[y][x]
            # pixel intensity값으로 해당 위치의 높이값을 계산한다.
            z = (pixel_intensity * max_height) / max_pix
            # 특정 위치의 높이값을 다음과 같이 설정한다.
            if z != 0:
                vertices[y][x] = (x, y, z)

    faces = []

    # face를 다음과 같이 만든다.
    for x in range(0, ncols - 1):
        for y in range(0, nrows - 1):
            # create face 1
            vertice1 = vertices[y][x]
            vertice2 = vertices[y + 1][x]
            vertice3 = vertices[y + 1][x + 1]
            if not (all(vertice1[:1] == (0, 0))
                    or all(vertice2[:1] == (0, 0))
                    or all(vertice3[:1] == (0, 0))):
                face1 = np.array([vertice1, vertice2, vertice3])
            else:
                face1 = None

            # create face 2
            vertice1 = vertices[y][x]
            vertice2 = vertices[y][x + 1]
            vertice3 = vertices[y + 1][x + 1]

            if not (all(vertice1[:1] == (0, 0))
                    or all(vertice2[:1] == (0, 0))
                    or all(vertice3[:1] == (0, 0))):
                face2 = np.array([vertice1, vertice2, vertice3])
            else:
                face2 = None

            if face1 is not None:
                faces.append(face1)
            if face2 is not None:
                faces.append(face2)

    facesNp = np.array(faces)
    print(facesNp.shape)
    # Create the mesh
    surface = mesh.Mesh(np.zeros(facesNp.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            surface.vectors[i][j] = facesNp[i][j]
            surface.ve
    # Write the mesh to file "cube.stl"
    surface.save(out_stl_path)


png2stl("images/aerial_image_antialiased.png", "stl/cup.stl")
