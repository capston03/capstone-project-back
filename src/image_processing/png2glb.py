from pathlib import Path

import open3d
from PIL import Image
from typing import Tuple
from pygltflib.utils import glb2gltf, gltf2glb
import numpy as np

# Convert png to glb.
from image_processing.image_utility import ImageUtility


class PNG2GLB:
    def __init__(self, png_path: str, glb_path: str, min_height: int, max_height: int, max_size: Tuple[int, int]):
        self.__png_path = Path(png_path)
        self.__glb_path = Path(glb_path)
        self.__min_height = min_height
        self.__max_height = max_height
        self.__max_size = max_size
        self.__front_vertices_1d = np.array([])
        self.__front_vertices_2d = np.array([])
        self.__front_triangles = np.array([])
        self.__back_vertices_1d = np.array([])
        self.__back_vertices_2d = np.array([])
        self.__back_triangles = np.array([])
        self.__color_map = np.array([])
        self.__mesh = open3d.geometry.TriangleMesh()

    def __init_front_vertices(self, img_mtr: np.ndarray):
        ncols, nrows = img_mtr.shape

        vertices_1d = []
        for x in range(0, nrows):
            for y in range(0, ncols):
                if img_mtr[y][x] != -1 and img_mtr[y][x] != 0:
                    vertices_1d.append([x, y, self.__max_height])
                elif img_mtr[y][x] == 0:
                    vertices_1d.append([x, y, 0])
                else:
                    vertices_1d.append([x, y, self.__min_height])
        vertices_2d = [vertices_1d[i:i + ncols] for i in range(0, len(vertices_1d), ncols)]
        self.__front_vertices_1d = np.array(vertices_1d)
        self.__front_vertices_2d = np.array(vertices_2d)

    def __init_back_vertices(self, img_mtr: np.ndarray):
        ncols, nrows = img_mtr.shape

        vertices_1d = []
        for x in range(0, nrows):
            for y in range(0, ncols):
                if img_mtr[y][x] != 0:
                    vertices_1d.append([x, y, self.__min_height])
                else:
                    vertices_1d.append([x, y, 0])
        vertices_2d = [vertices_1d[i:i + ncols] for i in range(0, len(vertices_1d), ncols)]
        self.__back_vertices_1d = np.array(vertices_1d)
        self.__back_vertices_2d = np.array(vertices_2d)

    def __init_mesh_vertices(self):
        mesh_vertices = np.concatenate((self.__front_vertices_1d, self.__back_vertices_1d), axis=0)
        self.__mesh.vertices = open3d.utility.Vector3dVector(mesh_vertices)

    def __init_front_triangles(self):
        nrows, ncols = self.__front_vertices_2d.shape[:2]
        triangles = []
        for x in range(0, nrows - 1):
            for y in range(0, ncols - 1):
                # create face 1 ---
                #               |/
                vertice1 = self.__front_vertices_2d[x][y]
                vertice2 = self.__front_vertices_2d[x + 1][y]
                vertice3 = self.__front_vertices_2d[x][y + 1]
                if 0 not in {vertice1[2], vertice2[2], vertice3[2]}:
                    triangles.append([x * ncols + y, (x + 1) * ncols + y, x * ncols + (y + 1)])
                # create face 2 /|
                #              /ㅡ|
                vertice1 = self.__front_vertices_2d[x][y + 1]
                vertice2 = self.__front_vertices_2d[x + 1][y]
                vertice3 = self.__front_vertices_2d[x + 1][y + 1]
                if 0 not in {vertice1[2], vertice2[2], vertice3[2]}:
                    triangles.append([x * ncols + (y + 1), (x + 1) * ncols + y, (x + 1) * ncols + (y + 1)])

        self.__front_triangles = np.array(triangles)

    def __init_back_triangles(self):
        nrows, ncols = self.__back_vertices_2d.shape[:2]
        triangles = []
        for x in range(0, nrows - 1):
            new_x = x + self.__front_vertices_2d.shape[0]
            for y in range(0, ncols - 1):
                # create face 1 ---
                #               |/
                vertice1 = self.__back_vertices_2d[x][y + 1]
                vertice2 = self.__back_vertices_2d[x + 1][y]
                vertice3 = self.__back_vertices_2d[x][y]
                if 0 not in {vertice1[2], vertice2[2], vertice3[2]}:
                    triangles.append([new_x * ncols + y + 1, (new_x + 1) * ncols + y + 1, new_x * ncols + y])
                # create face 2 /|
                #              /ㅡ|
                vertice1 = self.__back_vertices_2d[x][y]
                vertice2 = self.__back_vertices_2d[x + 1][y + 1]
                vertice3 = self.__back_vertices_2d[x + 1][y]
                if 0 not in {vertice1[2], vertice2[2], vertice3[2]}:
                    triangles.append([new_x * ncols + y, (new_x + 1) * ncols + y + 1, (new_x + 1) * ncols + y])

        self.__back_triangles = np.array(triangles)

    def __init_mesh_triangles(self):
        mesh_triangles = np.concatenate((self.__front_triangles, self.__back_triangles), axis=0)
        self.__mesh.triangles = open3d.utility.Vector3iVector(mesh_triangles.astype(np.int32))

    def __init_color_map(self, texture_mtr: np.ndarray):
        color_map = []
        ncols, nrows = texture_mtr.shape[:2]
        for i in range(nrows):
            for j in range(ncols):
                color = texture_mtr[j][i]
                color_map.append(color / 255)
        for i in range(nrows, nrows * 2):
            for j in range(ncols, ncols * 2):
                color = [213 / 255, 213 / 255, 213 / 255]
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
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        img.thumbnail(self.__max_size)
        alpha_mtr = np.array(img.convert("RGBA"))[..., 3]
        filter_mtr = np.where(alpha_mtr == 0, 0, 1)
        grey_img = img.convert("L")
        grey_img_mtr = np.array(grey_img)
        # Black area != Transparent area
        grey_img_mtr = np.where(grey_img_mtr == 0, 2, grey_img_mtr)
        # Filter the transparent area.
        grey_img_mtr = grey_img_mtr * filter_mtr
        grey_img_mtr = grey_img_mtr.astype("uint8")
        img_border_mtr = ImageUtility.get_border_line(grey_img_mtr)
        grey_img_mtr = np.where(img_border_mtr == 255, -1, grey_img_mtr)

        self.__init_front_vertices(grey_img_mtr)
        self.__init_back_vertices(grey_img_mtr)
        self.__init_mesh_vertices()
        self.__init_front_triangles()
        self.__init_back_triangles()
        self.__init_mesh_triangles()

        texture = Image.open(self.__png_path).convert("RGB")
        texture = texture.transpose(Image.FLIP_LEFT_RIGHT)
        texture = ImageUtility.enhance_color(texture)
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
