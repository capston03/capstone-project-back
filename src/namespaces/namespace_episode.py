from multiprocessing import Process
from typing import Dict, Final, Tuple

from flask import request
from flask_restx import Namespace, Resource

from image_processing.png2glb import PNG2GLB
from image_processing.image_utility import grabcut
from model.episode import Episode
from model.sticker import Sticker
from utility.utilities import check_if_param_has_keys, to_json, make_log_message, make_error_message
from datetime import datetime
from uuid import uuid4
from handler.S3_handler import handler as s3_handler
from handler.episode_DB_handler import episode_DB_handler
from handler.sticker_DB_handler import sticker_DB_handler

namespace_episode = Namespace("episode", "Api for episode")

INDEX_EPISODE_ID: Final = 0


def make_sticker(local_original_img_path: str, remote_original_img_path: str,
                 local_thumbnail_path: str, remote_thumbnail_path: str,
                 local_sticker_path: str, remote_sticker_path: str,
                 min_height: int, max_height: int, max_size: Tuple[int, int],
                 x_ratio: float, y_ratio: float, width_ratio: float, height_ratio: float):
    print(make_log_message("Save the original image into remote storage"))
    s3_handler.upload(local_original_img_path, remote_original_img_path)

    print(make_log_message("Remove background [In progress]"))
    grabcut(local_original_img_path, local_thumbnail_path, x_ratio, y_ratio, width_ratio, height_ratio)
    print(make_log_message("Remove background [Complete]"))
    s3_handler.upload(local_thumbnail_path, remote_thumbnail_path)

    print(make_log_message("Build the .GLB model [In progress]"))
    PNG2GLB(local_thumbnail_path, local_sticker_path, min_height, max_height, max_size).run()
    print(make_log_message("Build the .GLB model [Complete]"))
    s3_handler.upload(local_sticker_path, remote_sticker_path)


@namespace_episode.route("/upload")
class Upload(Resource):
    PREFIX_PATH_LOCAL_ORIGNAL_IMG: Final[str] = "./data/original_img/"
    PREFIX_PATH_REMOTE_ORIGNAL_IMG: Final[str] = "original_img/"
    PREFIX_PATH_LOCAL_THUMBNAIL: Final[str] = "./data/thumbnail/"
    PREFIX_PATH_REMOTE_THUMBNAIL: Final[str] = "thumbnail/"
    PREFIX_PATH_LOCAL_STICKER: Final[str] = "./data/sticker/"
    PREFIX_PATH_REMOTE_STICKER: Final[str] = "sticker/"

    def post(self):
        title = request.form["title"]
        content = request.form["content"]
        uploader_gmail_id = request.form["uploader_gmail_id"]
        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        beacon_mac = request.form["beacon_mac"]
        episode = Episode(title, content, uploader_gmail_id, upload_time, beacon_mac)
        try:
            episode_id = episode_DB_handler.write(episode)
        except Exception as e:
            print(str(e))
            return to_json("write_episode_db_failure")

        image = request.files["image"]
        unique_filename = f"{uploader_gmail_id}-{upload_time}-{uuid4()}"
        foreground_rectangle = [float(val) for val in request.form.getlist("foreground_rectangle[]")]
        local_original_img_path = f'{Upload.PREFIX_PATH_LOCAL_ORIGNAL_IMG}{unique_filename}.png'
        remote_original_img_path = f'{Upload.PREFIX_PATH_REMOTE_ORIGNAL_IMG}{unique_filename}.png'
        local_thumbnail_path = f"{Upload.PREFIX_PATH_LOCAL_THUMBNAIL}{unique_filename}.png"
        remote_thumbnail_path = f'{Upload.PREFIX_PATH_REMOTE_THUMBNAIL}{unique_filename}.png'
        local_sticker_path = f"{Upload.PREFIX_PATH_LOCAL_STICKER}{unique_filename}.glb"
        remote_sticker_path = f"{Upload.PREFIX_PATH_REMOTE_STICKER}{unique_filename}.glb"
        sticker = Sticker(remote_original_img_path, remote_thumbnail_path,
                          remote_sticker_path, foreground_rectangle, episode_id)
        try:
            sticker_id = sticker_DB_handler.write(sticker)
        except Exception as e:
            print(str(e))
            return to_json("write_sticker_db_failure")

        print(make_log_message("Save the original image into local storage"))
        image.save(local_original_img_path)
        process_making_sticker = Process(target=make_sticker,
                                         args=(local_original_img_path, remote_original_img_path,
                                               local_thumbnail_path, remote_thumbnail_path,
                                               local_sticker_path, remote_sticker_path,
                                               1, 21, (500, 500), *foreground_rectangle))
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
        try:
            episode = episode_DB_handler.read(params.get("episode_id"))
        except Exception as e:
            print(str(e))
            return to_json("error")
        return to_json(episode.__dict__)


@namespace_episode.route("/find_episodes_nearby_beacon")
class FindEpisodesNearbyBeacon(Resource):
    def post(self):
        try:
            beacon_mac = request.form["beacon_mac"]
            already_downloaded_episode_id_list = [int(val) for val in
                                                  request.form.getlist("already_downloaded_episode_id[]")]
        except Exception as e:
            print(make_error_message(str(e)))
            return to_json("error")
        try:
            episodes = episode_DB_handler.find_episodes_nearby_beacon(beacon_mac)
            episodes = [episode for episode in episodes
                        if episode.identifier not in already_downloaded_episode_id_list]
        except Exception as e:
            print(str(e))
            return to_json("error")
        return to_json({index: episode.__dict__
                        for index, episode in enumerate(episodes)})


@namespace_episode.route("/find_user_episodes")
class FindUserEpisodes(Resource):
    def post(self):
        if not request.is_json:
            return to_json('not_json')
        params: Dict[str, str] = request.get_json()
        if not check_if_param_has_keys(params, ["uploader_gmail_id"]):
            return to_json('invalid_input')
        try:
            episodes = episode_DB_handler.find_user_episodes(params.get("uploader_gmail_id"))
        except Exception as e:
            print(str(e))
            return to_json("error")
        return to_json({index: episode.__dict__
                        for index, episode in enumerate(episodes)})
