from multiprocessing import Process
from typing import Dict

from flask import request
from flask_restx import Namespace, Resource

from image_processing.grabcut import grabcut
from model.sticker import Sticker
from utility.utilities import check_if_param_has_keys, to_json
from datetime import datetime
from uuid import uuid4
from handler.handler_s3 import handler as s3_handler
from handler.handler_sticker_db import handler_sticker_db, HandlerStickerDB

namespace_sticker = Namespace('sticker', 'Api for sticker')

origin_img = "images/input_ex.jpeg"
output_img = "images/output_ex.jpeg"

# Foreground rectangle
(x, y, w, h) = (47, 78, 323, 246)
start = (x, y)
end = (x + w, y + h)
rect = (x, y, w, h)


def work(local_orig_path: str, local_sticker_path: str,
         start_x: float, start_y: float, width: float, height: float):
    grabcut(local_orig_path, local_sticker_path, start_x, start_y, width, height)


@namespace_sticker.route('/upload')
class Upload(Resource):
    def post(self):
        # Info
        image = request.files["image"]
        uploader_gmail_id = request.form['uploader_gmail_id']
        rectangle = request.form.getlist("rectangle")
        beacon_mac = request.form['beacon_mac']
        event_id = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())

        # Upload the image file
        ext = image.filename.split('.')[-1]
        filename = uploader_gmail_id + event_id + '.' + ext
        local_orig_path = f'./orig/{filename}'
        local_sticker_path = f'./sticker/{filename}'
        remote_orig_path = f'orig/{filename}'
        remote_sticker_path = f'sticker/{filename}'
        sticker = Sticker(uploader_gmail_id + event_id, remote_orig_path, remote_sticker_path, uploader_gmail_id,
                          datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                          beacon_mac, rectangle)
        image.save(local_orig_path)
        rc = s3_handler.upload(local_orig_path, remote_orig_path)
        if not rc:
            return to_json("failure")
        if not handler_sticker_db.write_info(sticker):
            return to_json("failure")
        p = Process(target=work, args=(local_orig_path, local_sticker_path, *rectangle))
        p.start()
        return to_json("success")
