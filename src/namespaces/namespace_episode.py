from multiprocessing import Process
from pathlib import Path
from typing import Dict, Final, Tuple

from flask import request
from flask_restx import Namespace, Resource

from image_processing.png2glb import PNG2GLB
from image_processing.image_utility import grabcut
from model.episode import Episode
from model.sticker import Sticker
from utility.utilities import check_if_param_has_keys, to_json
from datetime import datetime
from uuid import uuid4
from handler.handler_s3 import handler as s3_handler
from handler.handler_episode_db import handler_episode_db
from handler.handler_sticker_db import handler_sticker_db

namespace_episode = Namespace("episode", "Api for episode")

INDEX_EPISODE_ID: Final = 0


@namespace_episode.route("/upload")
class Upload(Resource):
    PREFIX_PATH_LOCAL_ORIGNAL_IMG: Final[str] = "./original_img/"
    PREFIX_PATH_REMOTE_ORIGNAL_IMG: Final[str] = "original_img/"
    PREFIX_PATH_LOCAL_THUMBNAIL: Final[str] = "./thumbnail/"
    PREFIX_PATH_REMOTE_THUMBNAIL: Final[str] = "thumbnail/"
    PREFIX_PATH_LOCAL_STICKER: Final[str] = "./sticker/"
    PREFIX_PATH_REMOTE_STICKER: Final[str] = "sticker/"

    @staticmethod
    def make_sticker(image, local_original_img_path: str, remote_original_img_path: str,
                     local_thumbnail_path: str, remote_thumbnail_path: str,
                     local_sticker_path: str, remote_sticker_path: str,
                     min_height: int, max_height: int, max_size: Tuple[int, int],
                     x_ratio: float, y_ratio: float, width_ratio: float, height_ratio: float):
        print("Save the original image into local/remote storage")
        image.save(local_original_img_path)
        # s3_handler.upload(local_original_img_path, remote_original_img_path)

        print("Remove background [In progress]")
        grabcut(local_original_img_path, local_thumbnail_path, x_ratio, y_ratio, width_ratio, height_ratio)
        print("Remove background [Complete]")
        # s3_handler.upload(local_thumbnail_path, remote_thumbnail_path)

        print("Build the .GLB model [In progress]")
        PNG2GLB(local_thumbnail_path, local_sticker_path, min_height, max_height, max_size).run()
        print("Build the .GLB model [Complete]")
        # s3_handler.upload(local_sticker_path, remote_sticker_path)

    def post(self):
        title = request.form["title"]
        content = request.form["content"]
        uploader_gmail_id = request.form["uploader_gmail_id"]
        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        beacon_mac = request.form["beacon_mac"]
        episode = Episode(title, content, uploader_gmail_id, upload_time, beacon_mac)
        episode_id, ok = handler_episode_db.write(episode)
        if not ok:
            return to_json("write_episode_db_failure")

        image = request.files["image"]
        unique_filename = f"{uploader_gmail_id}-{upload_time}-{uuid4()}"
        foreground_rectangle = request.form.getlist("foreground_rectangle[]")
        local_original_img_path = f'{Upload.PREFIX_PATH_LOCAL_ORIGNAL_IMG}{unique_filename}.png'
        remote_original_img_path = f'{Upload.PREFIX_PATH_REMOTE_ORIGNAL_IMG}{unique_filename}.png'
        local_thumbnail_path = f"{Upload.PREFIX_PATH_LOCAL_THUMBNAIL}{unique_filename}.png"
        remote_thumbnail_path = f'{Upload.PREFIX_PATH_REMOTE_THUMBNAIL}{unique_filename}.png'
        local_sticker_path = f"{Upload.PREFIX_PATH_LOCAL_STICKER}{unique_filename}.glb"
        remote_sticker_path = f"{Upload.PREFIX_PATH_REMOTE_STICKER}{unique_filename}.glb"
        sticker = Sticker(remote_original_img_path, remote_thumbnail_path,
                          remote_sticker_path, foreground_rectangle, episode_id)
        sticker_id, ok = handler_sticker_db.write(sticker)
        if not ok:
            return to_json("write_sticker_db_failure")
        process_making_sticker = Process(target=Upload.make_sticker,
                                         args=(image, local_original_img_path, remote_original_img_path,
                                               local_thumbnail_path, remote_thumbnail_path,
                                               local_sticker_path, remote_sticker_path,
                                               10, 20, (500, 500), *foreground_rectangle))
        process_making_sticker.start()
        return to_json("success")


@namespace_episode.route("/download")
class Download(Resource):
    def post(self):
        if not request.is_json:
            return to_json('not_json')
        params: Dict[str, str] = request.get_json()
        if not check_if_param_has_keys(params, ["episode_id"]):
            return to_json('invalid_input')
        episode = handler_episode_db.read(params.get("episode_id"))
        return to_json(episode.__dict__)


@namespace_episode.route("/find_episodes_nearby_beacon")
class FindEpisodesNearbyBeacon(Resource):
    def post(self):
        if not request.is_json:
            return to_json('not_json')
        params: Dict[str, str] = request.get_json()
        if not check_if_param_has_keys(params, ["beacon_mac"]):
            return to_json('invalid_input')
        episodes = handler_episode_db.find_episodes_nearby_beacon(params.get("beacon_mac"))
        return to_json({index: episode.__dict__
                        for index, episode in enumerate(episodes)})


@namespace_episode.route("/find_episodes_nearby_beacon")
class FindUserEpisodes(Resource):
    def post(self):
        if not request.is_json:
            return to_json('not_json')
        params: Dict[str, str] = request.get_json()
        if not check_if_param_has_keys(params, ["uploader_gmail_id"]):
            return to_json('invalid_input')
        episodes = handler_episode_db.find_user_episodes(params.get("uploader_gmail_id"))
        return to_json({index: episode.__dict__
                        for index, episode in enumerate(episodes)})
