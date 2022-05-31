from pathlib import Path

import open3d
import numpy as np
from PIL import Image
from typing import Tuple
from pygltflib.utils import glb2gltf, gltf2glb


# Convert png to glb.
class PNG2GLB:
    def __init__(self, png_path: str, glb_path: str, max_height: int, max_size: Tuple[int, int]):
        self.__png_path = Path(png_path)
        self.__glb_path = Path(glb_path)
        self.__max_height = max_height
        self.__max_size = max_size
        self.__vertices_1d = np.array([])
        self.__vertices_2d = np.array([])
        self.__triangles = np.array([])
        self.__color_map = np.array([])
        self.__mesh = open3d.geometry.TriangleMesh()

    def __init_vertices(self, img_mtr: np.ndarray):
        """
        Init 1-dimensional, 2-dimensional vertex list.
        Save them to instance property.
        :return: None
        """
        ncols, nrows = img_mtr.shape
        max_px_val = img_mtr.max()

        vertices_1d = []
        for x in range(0, nrows):
            for y in range(0, ncols):
                vertices_1d.append([x, y, img_mtr[y][x] * self.__max_height / max_px_val])
        vertices_2d = [vertices_1d[i:i + ncols] for i in range(0, len(vertices_1d), ncols)]
        self.__vertices_1d = np.array(vertices_1d)
        self.__vertices_2d = np.array(vertices_2d)
        self.__mesh.vertices = open3d.utility.Vector3dVector(self.__vertices_1d)

    def __init_triangles(self):
        """
        Init triangle list.
        Save it to instance property.
        :return: None
        """
        nrows, ncols = self.__vertices_2d.shape[:2]
        triangles = []
        for x in range(0, nrows - 1):
            for y in range(0, ncols - 1):
                # create face 1 ---
                #               |/
                vertice1 = self.__vertices_2d[x][y]
                vertice2 = self.__vertices_2d[x + 1][y]
                vertice3 = self.__vertices_2d[x][y + 1]
                if 0 not in {vertice1[2], vertice2[2], vertice3[2]}:
                    triangles.append([x * ncols + y, (x + 1) * ncols + y, x * ncols + (y + 1)])
                # create face 2 /|
                #              /ㅡ|
                vertice1 = self.__vertices_2d[x][y + 1]
                vertice2 = self.__vertices_2d[x + 1][y]
                vertice3 = self.__vertices_2d[x + 1][y + 1]
                if 0 not in {vertice1[2], vertice2[2], vertice3[2]}:
                    triangles.append([x * ncols + (y + 1), (x + 1) * ncols + y, (x + 1) * ncols + (y + 1)])
        self.__triangles = np.array(triangles)
        self.__mesh.triangles = open3d.utility.Vector3iVector(self.__triangles.astype(np.int32))

    def __init_color_map(self, texture_mtr: np.ndarray):
        """
        Init color map.
        Save it to instance property.
        :param texture_mtr: Texture (RGB)
        :return: None
        """
        color_map = []
        ncols, nrows = texture_mtr.shape[:2]
        for i in range(nrows):
            for j in range(ncols):
                color = texture_mtr[j][i]
                if np.linalg.norm(color) > 0:
                    color_map.append(list(color / np.linalg.norm(color)))
                else:
                    color_map.append(color)
        self.__color_map = np.array(color_map)
        self.__mesh.vertex_colors = open3d.utility.Vector3dVector(self.__color_map)

    def show(self):
        """
        Show the mesh.
        :return: None
        """
        open3d.visualization.draw_geometries([self.__mesh])

    def run(self):
        """
        Run the converter
        **mtr means matrix
        :return: None
        """
        img = Image.open(self.__png_path)
        img.thumbnail(self.__max_size)
        alpha_mtr = np.array(img.convert("RGBA"))[..., 3]
        filter_mtr = np.where(alpha_mtr == 0, 0, 1)
        grey_img = img.convert("L")
        grey_img_mtr = np.array(grey_img)
        # Black area != Transparent area
        grey_img_mtr = np.where(grey_img_mtr == 0, 2, grey_img_mtr)
        # Filter the transparent area.
        grey_img_mtr = grey_img_mtr * filter_mtr

        self.__init_vertices(grey_img_mtr)
        self.__init_triangles()

        texture = Image.open(self.__png_path).convert("RGB")
        texture.thumbnail(self.__max_size)
        texture_mtr = np.array(texture)
        self.__init_color_map(texture_mtr)
        self.__mesh.compute_vertex_normals()
        r = self.__mesh.get_rotation_matrix_from_xyz((0, 0, np.pi))
        self.__mesh.rotate(r, center=(0, 0, 0))
        # self.show()
        gltf_path = self.__glb_path.with_suffix(".gltf")
        open3d.io.write_triangle_mesh(str(gltf_path), self.__mesh)
        gltf2glb(str(gltf_path), override=True)
