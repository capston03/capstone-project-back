from multiprocessing import Process
from pathlib import Path
from typing import Dict, Final, Tuple

from flask import request
from flask_restx import Namespace, Resource

from image_processing.png2glb import PNG2GLB
from image_processing.grabcut import grabcut
from model.sticker import Sticker
from utility.utilities import check_if_param_has_keys, to_json
from datetime import datetime
from uuid import uuid4
from handler.handler_s3 import handler as s3_handler
from handler.handler_sticker_db import handler_sticker_db, HandlerStickerDB

namespace_sticker = Namespace('sticker', 'Api for sticker')
#
# origin_img = "images/input_ex.jpeg"
# output_img = "images/output_ex.jpeg"
#
# # Foreground rectangle
# (x, y, w, h) = (47, 78, 323, 246)
# start = (x, y)
# end = (x + w, y + h)
# rect = (x, y, w, h)

PREFIX_PATH_LOCAL_ORIG: Final[str] = "./orig/"
PREFIX_PATH_REMOTE_ORIG: Final[str] = "orig/"
PREFIX_PATH_LOCAL_STICKER: Final[str] = "./sticker/"
PREFIX_PATH_REMOTE_STICKER: Final[str] = "sticker/"
PREFIX_PATH_LOCAL_GLTF: Final[str] = "./glb/"
PREFIX_PATH_REMOTE_GLTF: Final[str] = "glb/"


def work(filename: str, max_height: int, max_size: Tuple[int, int], x_ratio: float, y_ratio: float, width_ratio: float,
         height_ratio: float):
    local_orig_path = PREFIX_PATH_LOCAL_ORIG + filename
    local_sticker_path = PREFIX_PATH_LOCAL_STICKER + filename
    remote_sticker_path = PREFIX_PATH_REMOTE_STICKER + filename
    grabcut(local_orig_path, local_sticker_path, x_ratio, y_ratio, width_ratio, height_ratio)
    s3_handler.upload(local_sticker_path, remote_sticker_path)
    print("Remove background Complete...")
    gltf_filename = str(Path(filename).with_suffix(".glb"))
    local_glb_path = PREFIX_PATH_LOCAL_GLTF + gltf_filename
    remote_glb_path = PREFIX_PATH_REMOTE_GLTF + gltf_filename
    PNG2GLB(local_sticker_path, local_glb_path, max_height, max_size).run()
    s3_handler.upload(local_glb_path, remote_glb_path)
    print("Build the gltf model Complete!")


@namespace_sticker.route('/upload')
class Upload(Resource):
    def post(self):
        # Info
        image = request.files["image"]
        uploader_gmail_id = request.form['uploader_gmail_id']
        rectangle = [float(e) for e in request.form.getlist("rectangle[]")]
        beacon_mac = request.form['beacon_mac']
        event_id = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())

        # Upload the image file
        filename = uploader_gmail_id + event_id + '.' + "png"
        local_orig_path = f'{PREFIX_PATH_LOCAL_ORIG}{filename}'
        remote_orig_path = f'{PREFIX_PATH_REMOTE_ORIG}{filename}'
        remote_sticker_path = f'{PREFIX_PATH_REMOTE_STICKER}{filename}'
        remote_glb_path = f"{PREFIX_PATH_REMOTE_GLTF}{filename}"
        sticker = Sticker(uploader_gmail_id + event_id,
                          remote_orig_path, remote_sticker_path,
                          remote_glb_path, uploader_gmail_id,
                          datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                          beacon_mac, rectangle)
        image.save(local_orig_path)
        rc = s3_handler.upload(local_orig_path, remote_orig_path)
        if not rc:
            return to_json("upload_to_s3_failure")
        if not handler_sticker_db.write_info(sticker):
            return to_json("write_db_failure")
        p = Process(target=work, args=(filename, 30, (500, 500), *rectangle))
        p.start()
        return to_json("success")
