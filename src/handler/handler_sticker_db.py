from enum import Enum, auto
from typing import Final

from model.sticker import Sticker
from .handler_db import handler_db as db_handler, HandlerDB


class HandlerStickerDB:
    class State(Enum):
        UNKNOWN_ERROR = auto()
        OK = auto()
        FULL = auto()
        NEED_TO_ADD = auto()
        EXISTED = auto()

    def __init__(self, db_handler: HandlerDB):
        self.db_handler = db_handler

    def __connect_db(self):
        return self.db_handler.connect_db()

    RANGE_RADIUS: Final[int] = 5

    # Write sticker info into DB
    def write_info(self, sticker: Sticker):
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"INSERT INTO sticker (id, orig_img_path, " \
                          f"sticker_path, uploader_gmail_id, " \
                          f"upload_time, foreground_rect) " \
                          f"VALUES('{sticker.id}', " \
                          f"'{sticker.orig_img_path}', " \
                          f"'{sticker.sticker_path}', " \
                          f"'{sticker.uploader_gmail_id}', " \
                          f"'{sticker.upload_time}', " \
                          f"'{sticker.foreground_rect}')"
                    cursor.execute(sql)
                    db.commit()
                    return HandlerStickerDB.State.OK
            except Exception as e:
                print(f"error : {e}")
                return HandlerStickerDB.State.UNKNOWN_ERROR


handler_sticker_db = HandlerStickerDB(db_handler)
