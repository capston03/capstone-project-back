from enum import Enum, auto
from typing import Tuple

from model.episode import Episode
from model.sticker import Sticker
from DB_handler import DB_handler, DBHandler
from utility.utilities import make_error_message


# Handler for handling db about sticker image
class StickerDBHandler:

    def __init__(self, _DB_handler: DBHandler):
        self.__DB_handler = _DB_handler

    def __connect_db(self):
        return self.__DB_handler.connect()

    @staticmethod
    def __convert_raw_db_data_to_sticker_instance(raw_data):
        return Sticker(raw_data[2], raw_data[3], raw_data[4],
                       [float(val) for val in raw_data[5].split(" ")], raw_data[1], raw_data[0])

    def read(self, sticker_id: str):
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT * FROM sticker " \
                          f"WHERE id = '{sticker_id}';"
                    cursor.execute(sql)
                    raw_data = cursor.fetchone()
                    return self.__convert_raw_db_data_to_sticker_instance(raw_data)
            except Exception as e:
                raise Exception(make_error_message(str(e)))

    def write(self, sticker: Sticker) -> int:
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"INSERT INTO sticker (episode_id, " \
                          f"original_img_path, thumbnail_path, sticker_path, " \
                          f"foreground_rectangle) " \
                          f"VALUES('{sticker.episode_id}', " \
                          f"'{sticker.original_img_path}', " \
                          f"'{sticker.thumbnail_path}', " \
                          f"'{sticker.sticker_path}', " \
                          f"'{sticker.foreground_rectangle}');"
                    cursor.execute(sql)
                    db.commit()
                    sticker_id = int(cursor.lastrowid)
                    return sticker_id
            except Exception as e:
                raise Exception(make_error_message(str(e)))

    def find_episode_stickers(self, episode_id: int):
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT * FROM sticker " \
                          f"WHERE episode_id = {episode_id};"
                    cursor.execute(sql)
                    raw_data = cursor.fetchone()
                    return self.__convert_raw_db_data_to_sticker_instance(raw_data)
            except Exception as e:
                raise Exception(make_error_message(str(e)))


sticker_DB_handler = StickerDBHandler(DB_handler)
