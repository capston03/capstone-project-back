from enum import Enum, auto
from typing import Final

from model.sticker import Sticker
from .handler_db import handler_db, HandlerDB


# Handler for handling db about sticker image
class HandlerStickerDB:

    def __init__(self, handler_db: HandlerDB):
        self.handler_db = handler_db

    def __connect_db(self):
        """
        Connect to the database.
        :return: Connection
        """
        return self.handler_db.connect_db()

    # Write sticker info into DB
    def write_info(self, sticker: Sticker) -> bool:
        """
        Write information about sticker image into the database.
        :param sticker: Information about sticker image
        :return: Connection
        """
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"INSERT INTO sticker (id, img_path, " \
                          f"sticker_path, glb_path, uploader_gmail_id, " \
                          f"upload_time, beacon_mac, foreground_rect) " \
                          f"VALUES('{sticker.id}', " \
                          f"'{sticker.img_path}', " \
                          f"'{sticker.sticker_path}'," \
                          f"'{sticker.glb_path}', " \
                          f"'{sticker.uploader_gmail_id}', " \
                          f"'{sticker.upload_time}', " \
                          f"'{sticker.beacon_mac}', " \
                          f"'{sticker.foreground_rect}')"
                    cursor.execute(sql)
                    db.commit()
                    return True
            except Exception as e:
                print(f"error : {e}")
                return False

    def get_sticker_nearby(self, beacon_mac):
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT * FROM sticker " \
                          f"WHERE beacon_mac = '{beacon_mac}';"
                    cursor.execute(sql)
                    return list(cursor.fetchall())
            except Exception as e:
                print(f"error : {e}")
                return []

    def get_user_sticker(self, gmail_id: str):
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT * FROM sticker " \
                          f"WHERE uploader_gmail_id = '{gmail_id}';"
                    cursor.execute(sql)
                    return list(cursor.fetchall())
            except Exception as e:
                print(f"error : {e}")
                return []


handler_sticker_db = HandlerStickerDB(handler_db)
