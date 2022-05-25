import open3d
import numpy as np
from PIL import Image

# mesh = open3d.geometry.TriangleMesh()
# np_vertices = np.array([[2, 2, 0],
#                         [5, 2, 0],
#                         [5, 5, 0]])
# np_triangles = np.array([[0, 1, 2]]).astype(np.int32)
#
# mesh.vertices = open3d.utility.Vector3dVector(np_vertices)
#
# mesh.triangles = open3d.utility.Vector3iVector(np_triangles)
#
# open3d.visualization.draw_geometries([mesh])
#
# # From Open3D to numpy
# np_triangles = np.asarray(mesh.triangles)
# print(np_triangles)

src_im_path = "images/aerial_image_antialiased.png"
grey_im = Image.open(src_im_path).convert("L")
max_size = (500, 500)
max_height = 50
min_height = 0

# max_size 사이즈로 섬네일 제작.
grey_im.thumbnail(max_size)
# 읽은 이미지를 numpy 배열로 변환.
im_mtr = np.array(grey_im).T
# 이미지 배열의 최소값, 최대값을 추출.
max_pix = im_mtr.max()
# min_pix = im_mtr.min()
# 이미지 배열의 행 수, 열 수 추출.
ncols, nrows = grey_im.size


# 각 이미지 배열의 원소마다 3개의 원소가 할당된다.
# vertices = np.zeros((nrows, ncols, 3))

def compute_vertex_elem(x, y):
    return (x, y, im_mtr[x][y] * max_height / max_pix)


vertices_1d: np.ndarray = np.fromfunction(lambda x, y: (x, y, im_mtr[x][y] * max_height / max_pix),
                                          (nrows * ncols, 3), dtype=float)
vertices_2d: np.ndarray = vertices_1d.reshape((nrows, ncols))
triangles = []
for x in range(0, nrows - 1):
    for y in range(0, ncols - 1):
        vertice1 = vertices_2d[x][y]
        vertice2 = vertices_2d[x + 1][y]
        vertice3 = vertices_2d[x + 1][y + 1]
        if 0 not in {vertice1[2], vertice2[2], vertice3[2]}:
            triangles.append(np.array([x * y, (x + 1) * y, (x + 1) * (y + 1)]))
        # create face 2
        vertice1 = vertices_2d[x][y]
        vertice2 = vertices_2d[x][y + 1]
        vertice3 = vertices_2d[x + 1][y + 1]
        if 0 not in {vertice1[2], vertice2[2], vertice3[2]}:
            triangles.append(np.array([x * y, x * (y + 1), (x + 1) * (y + 1)]))

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
