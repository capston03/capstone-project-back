from PIL import Image
import matplotlib.pyplot as plt


class PixelArtGenerator:
    def __init__(self, orig_img_path: str, out_img_path: str, resize_ratio: float):
        self.__orig_img_path = orig_img_path
        self.__out_img_path = out_img_path
        self.__resize_ratio = resize_ratio

    def run(self):
        img = Image.open(self.__orig_img_path)
        orig_size = (img.width, img.height)
        resized_size = (int(img.width * self.__resize_ratio),
                        int(img.height * self.__resize_ratio))
        small_img = img.resize(resized_size, Image.BILINEAR)
        pixeled_img = small_img.resize(orig_size, Image.NEAREST)
        pixeled_img.save(self.__out_img_path)
        plt.imshow(pixeled_img)
        plt.show()


generator = PixelArtGenerator('images/pixel_art_example.jpeg',
                              'images/pixel_art_example_output.jpeg',
                              0.5)
generator.run()
