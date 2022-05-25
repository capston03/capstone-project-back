import open3d
import numpy as np
from PIL import Image
import copy


def make_vertices(img_mtr: np.ndarray, max_height: int):
    ncols, nrows = img_mtr.shape
    max_px_val = img_mtr.max()

    vertices_1d = []
    for x in range(0, nrows):
        for y in range(0, ncols):
            vertices_1d.append([x, y, img_mtr[y][x] * max_height / max_px_val])
    vertices_2d = [vertices_1d[i:i + ncols] for i in range(0, len(vertices_1d), ncols)]
    return np.array(vertices_1d), np.array(vertices_2d)


def make_triangles(vertices_2d):
    nrows, ncols = vertices_2d.shape[:2]
    triangles = []
    for x in range(0, nrows - 1):
        for y in range(0, ncols - 1):
            # create face 1 ---
            #               |/
            vertice1 = vertices_2d[x][y]
            vertice2 = vertices_2d[x + 1][y]
            vertice3 = vertices_2d[x][y + 1]
            if 0 not in {vertice1[2], vertice2[2], vertice3[2]}:
                triangles.append([x * ncols + y, (x + 1) * ncols + y, x * ncols + (y + 1)])
            # create face 2 /|
            #              /ㅡ|
            vertice1 = vertices_2d[x][y + 1]
            vertice2 = vertices_2d[x + 1][y]
            vertice3 = vertices_2d[x + 1][y + 1]
            if 0 not in {vertice1[2], vertice2[2], vertice3[2]}:
                triangles.append([x * ncols + (y + 1), (x + 1) * ncols + y, (x + 1) * ncols + (y + 1)])
    return np.array(triangles)


def make_color_map(texture_mtr):
    color_map = []
    ncols, nrows = texture_mtr.shape[:2]
    for i in range(nrows):
        for j in range(ncols):
            color = texture_mtr[j][i]
            if np.linalg.norm(color) > 0:
                color_map.append(list(color / np.linalg.norm(color)))
            else:
                color_map.append(color)
    return np.array(color_map)


def to_glb(src_png_path: str, out_glb_path: str):
    alpha_mtr = np.array(Image.open(src_png_path).convert("RGBA"))[..., 3]
    filter_mtr = np.where(alpha_mtr == 0, 0, 1)
    grey_img = Image.open(src_png_path).convert("L")
    max_size = (500, 500)
    grey_img.thumbnail(max_size)
    grey_img_mtr = np.array(grey_img)
    # Do not consider the black area as transparent area.
    grey_img_mtr = np.where(grey_img_mtr == 0, 1, grey_img_mtr)
    # Filter the transparent area.
    grey_img_mtr = grey_img_mtr * filter_mtr
    bottom_img_mtr = copy.deepcopy(grey_img_mtr)
    # Set the z value of bottom plane to 0.
    bottom_img_mtr = np.where(bottom_img_mtr != 0, 1, 0)

    max_height = 50
    obj_vertices_1d, obj_vertices_2d = make_vertices(grey_img_mtr, max_height)
    obj_triangles = make_triangles(obj_vertices_2d)

    bottom_vertices_1d, bottom_vertices_2d = make_vertices(bottom_img_mtr, 1)
    bottom_triangles = make_triangles(bottom_vertices_2d)

    vertices_1d = np.concatenate([obj_vertices_1d, bottom_vertices_1d])
    triangles = np.concatenate([obj_triangles, bottom_triangles])
    mesh = open3d.geometry.TriangleMesh()
    mesh.vertices = open3d.utility.Vector3dVector(vertices_1d)
    mesh.triangles = open3d.utility.Vector3iVector(np.array(triangles).astype(np.int32))

    obj_texture = Image.open("../images/aerial_image_antialiased.png").convert("RGB")
    max_size = (500, 500)
    obj_texture.thumbnail(max_size)
    texture_mtr = np.array(obj_texture)

    obj_color_map = make_color_map(texture_mtr)
    bottom_color_map = np.zeros(obj_color_map.shape)
    bottom_color_map.fill(0.9)
    color_map = np.concatenate([obj_color_map, bottom_color_map])
    color_map = open3d.utility.Vector3dVector(np.array(color_map))
    mesh.vertex_colors = color_map
    mesh.compute_vertex_normals()

    open3d.visualization.draw_geometries([mesh])
    open3d.io.write_triangle_mesh(out_glb_path, mesh)


src_png_path = "../images/aerial_image_antialiased.png"
out_glb_path = "../gltf/cub.gltf"
to_glb(src_png_path, out_glb_path)
# mesh: open3d.geometry.TriangleMesh = open3d.io.read_triangle_mesh(out_glb_path)
