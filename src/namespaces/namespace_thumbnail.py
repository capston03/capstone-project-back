from typing import Dict, Final

from flask import request
from flask_restx import Namespace, Resource
from utility.utilities import check_if_param_has_keys, to_json
from handler.S3_handler import handler as s3_handler
from handler.sticker_DB_handler import sticker_DB_handler

namespace_thumbnail = Namespace('thumbnail', 'Api for thumbnail')


@namespace_thumbnail.route("/download")
class Download(Resource):
    def post(self):
        if not request.is_json:
            return to_json('not_json')
        params: Dict[str, str] = request.get_json()
        if not check_if_param_has_keys(params, ["episode_id"]):
            return to_json('invalid_input')
        try:
            sticker = sticker_DB_handler.find_episode_stickers(int(params.get("episode_id")))
        except Exception as e:
            print(str(e))
            return to_json("error")
        return to_json({"download_url": s3_handler.generate_download_url(sticker.thumbnail_path)})
