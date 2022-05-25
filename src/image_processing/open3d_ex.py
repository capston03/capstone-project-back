import open3d
import numpy as np

# Example mesh
# x, y coordinates:
# [0: (-1, 2)]__________[1: (1, 2)]
#             \        /\
#              \  (0) /  \
#               \    / (1)\
#                \  /      \
#      [2: (0, 0)]\/________\[3: (2, 0)]
#
# z coordinate: 0

# Example for open3d
# Do not use! (Deprecated)
mesh = open3d.geometry.TriangleMesh()
np_vertices = np.array([[-1, 2, 0],
                        [1, 2, 0],
                        [0, 0, 0],
                        [2, 0, 0]])
np_triangles = np.array([[0, 2, 1],
                         [1, 2, 3]]).astype(np.int32)
mesh.vertices = open3d.utility.Vector3dVector(np_vertices)

# From numpy to Open3D
mesh.triangles = open3d.utility.Vector3iVector(np_triangles)

# From Open3D to numpy
np_triangles = np.asarray(mesh.triangles)
open3d.visualization.draw_geometries([mesh])
