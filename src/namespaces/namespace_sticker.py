from typing import Dict

from flask import request
from flask_restx import Namespace, Resource

from image_processing.remove_bg import BgRemover
from model.sticker import Sticker
from utility.utilities import check_if_param_has_keys, to_json
from datetime import datetime
from uuid import uuid4
from handler.handler_s3 import handler as s3_handler
from handler.handler_sticker_db import handler_sticker_db, HandlerStickerDB
from multiprocessing import Process, Queue

namespace_sticker = Namespace('sticker', 'Api for sticker')

origin_img = "images/input_ex.jpeg"
output_img = "images/output_ex.jpeg"

(x, y, w, h) = (47, 78, 323, 246)
start = (x, y)
end = (x + w, y + h)
rect = (x, y, w, h)


def work(sticker: Sticker, start_x: float, start_y: float, width: float, height: float):
    orig_img_path = 'images/' + sticker.orig_img_path
    r = orig_img_path.split('.')
    o = r.copy()
    r.insert(-1, '_resized')
    o.insert(-1, '_out')
    resized_img_path = '.'.join(r)
    out_img_path = '.'.join(o)
    remover = BgRemover(orig_img_path, resized_img_path, out_img_path)
    remover.run(start_x, start_y, width, height)


@namespace_sticker.route('/upload')
class UploadOrig(Resource):
    def post(self):
        # Info
        image = request.files["image"]
        uploader_gmail_id = request.form['uploader_gmail_id']
        rectangle = request.form.getlist("rectangle")
        beacon_mac = request.form['beacon_mac']
        eventid = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())

        # Upload the image file
        ext = image.filename.split('.')[-1]
        filename = uploader_gmail_id + eventid + '.' + ext
        local_path = f'./images/{filename}'
        remote_path = f'sticker/{filename}'
        sticker = Sticker(uploader_gmail_id + eventid, filename, '', uploader_gmail_id,
                          datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                          beacon_mac, " ".join(rectangle))
        image.save(local_path)
        rc = s3_handler.upload(local_path, remote_path)
        if rc:
            state = handler_sticker_db.write_info(sticker)
            if state == HandlerStickerDB.State.OK:
                p = Process(target=work, args=(sticker, 47, 78, 323, 246))
                p.start()
                return to_json('success')
            else:
                return to_json('failure')
        else:
            return to_json('failure')
