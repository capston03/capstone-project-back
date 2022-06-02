from typing import Dict, Final, Tuple

from flask import request
from flask_restx import Namespace, Resource
from utility.utilities import check_if_param_has_keys, to_json
from handler.handler_s3 import handler as s3_handler
from handler.handler_sticker_db import handler_sticker_db

namespace_sticker = Namespace('sticker', 'Api for sticker')


@namespace_sticker.route("/download")
class Download(Resource):
    def post(self):
        if not request.is_json:
            return to_json('not_json')
        params: Dict[str, str] = request.get_json()
        if not check_if_param_has_keys(params, ["episode_id"]):
            return to_json('invalid_input')
        sticker = handler_sticker_db.find_episode_stickers(int(params.get("episode_id")))
        return to_json({"download_url": s3_handler.generate_download_url(sticker.sticker_path)})
