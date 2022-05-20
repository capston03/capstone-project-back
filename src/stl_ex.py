import numpy as np
from stl import mesh

# 8개의 선
# Define the 8 vertices of the cube
vertices = np.array([
    [-1, -1, -1],
    [+1, -1, -1],
    [+1, +1, -1],
    [-1, +1, -1],
    [-1, -1, +1],
    [+1, -1, +1],
    [+1, +1, +1],
    [-1, +1, +1]])

# 12개의 면
# 삼각형, 사각형 및 어떠한 도형도 가능하지만, 여기서는 삼각형으로 한다.
# Define the 12 triangles composing the cube
faces = np.array([
    [0, 3, 1],
    [1, 3, 2],
    [0, 4, 7],
    [0, 7, 3],
    [4, 5, 6],
    [4, 6, 7],
    [5, 1, 2],
    [5, 2, 6],
    [2, 3, 6],
    [3, 7, 6],
    [0, 1, 5],
    [0, 5, 4]])

# Create the mesh
cube = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
for i, f in enumerate(faces):
    # i = face의 index
    # f = face
    for j in range(3):
        # j = face 삼각형을 이루는 세 vertex 중 하나의 vertex index
        # face 삼각형을 이루는 하나의 vertex 출력
        print(vertices[f[j], :])
        # cube의 vector를 해당 vertex로 초기화한다.
        # 하나씩 하나씩 cube의 vector를 채워간다.
        cube.vectors[i][j] = vertices[f[j]]

# Write the mesh to file "cube.stl"
cube.save('cube.stl')
