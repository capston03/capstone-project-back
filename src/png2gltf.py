from pygltflib import GLTF2
from pygltflib.utils import ImageFormat, Image, gltf2glb

# gltf = GLTF2()
# image = Image()
# image.uri = "images/rm_black_bg.png"
# gltf.images.append(image)
# gltf.convert_images(ImageFormat.DATAURI)
# print(gltf.images[0].uri)
# print(gltf.images[0].name)
# gltf.save("test.gltf")
# gltf2glb("test.gltf", "test.glb")

gltf_path = "gltf/cube.gltf"
gltf = GLTF2.load(gltf_path)
gltf.export_image(0, "images/cube.png", override=True)
