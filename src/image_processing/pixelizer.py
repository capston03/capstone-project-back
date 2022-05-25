from PIL import Image


# Do not use. (Deprecated)
def pixelize(src_im_path: str, out_im_path: str, resize_ratio: float):
    img = Image.open(src_im_path)
    orig_size = (img.width, img.height)
    resized_size = (int(img.width * resize_ratio),
                    int(img.height * resize_ratio))
    small_img = img.resize(resized_size, Image.BILINEAR)
    pixeled_img = small_img.resize(orig_size, Image.NEAREST)
    pixeled_img.save(out_im_path)

# pixelize("images/grabcut_ex.png", "images/pixelized_output.png", 0.3)
