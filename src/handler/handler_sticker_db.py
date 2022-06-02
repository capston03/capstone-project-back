from enum import Enum, auto
from typing import Tuple

from model.episode import Episode
from model.sticker import Sticker
from .handler_db import handler_db, HandlerDB


# Handler for handling db about sticker image
class HandlerStickerDB:

    def __init__(self, handler_db: HandlerDB):
        self.handler_db = handler_db

    def __connect_db(self):
        return self.handler_db.connect_db()

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
                print(f"error : {e}")
                return None

    def write(self, sticker: Sticker) -> Tuple[int, bool]:
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
                    return sticker_id, True
            except Exception as e:
                print(f"error : {e}")
                return -1, False

    def find_stickers_nearby_beacon(self, beacon_mac: str):
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT * FROM sticker " \
                          f"WHERE beacon_mac = '{beacon_mac}';"
                    cursor.execute(sql)
                    raw_data_list = list(cursor.fetchall())
                    return [self.__convert_raw_db_data_to_sticker_instance(raw_data)
                            for raw_data in raw_data_list]
            except Exception as e:
                print(f"error : {e}")
                return []

    def find_user_stickers(self, uploader_gmail_id: str):
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT * FROM sticker " \
                          f"WHERE uploader_gmail_id = '{uploader_gmail_id}';"
                    cursor.execute(sql)
                    raw_data_list = cursor.fetchall()
                    return [self.__convert_raw_db_data_to_sticker_instance(raw_data)
                            for raw_data in raw_data_list]
            except Exception as e:
                print(f"error : {e}")
                return []

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
                print(f"error : {e}")
                return None


handler_sticker_db = HandlerStickerDB(handler_db)
