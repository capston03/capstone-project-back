from model.episode import Episode
from model.sticker import Sticker
from handler.handler_db import handler_db, HandlerDB
from typing import Tuple


class HandlerEpisodeDB:

    def __init__(self, handler_db: HandlerDB):
        self.handler_db = handler_db

    def __connect_db(self):
        return self.handler_db.connect_db()

    @staticmethod
    def __convert_raw_db_data_to_episode_instance(raw_data):
        return Episode(raw_data[1], raw_data[2], raw_data[3], str(raw_data[4]), raw_data[5], raw_data[0],
                       raw_data[6])

    def read(self, episode_id: int):
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT * FROM episode " \
                          f"WHERE id = '{episode_id}';"
                    cursor.execute(sql)
                    raw_data = cursor.fetchone()
                    return self.__convert_raw_db_data_to_episode_instance(raw_data)
            except Exception as e:
                print(f"error : {e}")
                return None

    def write(self, episode: Episode) -> Tuple[int, bool]:
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"INSERT INTO episode (title, content, uploader_gmail_id, " \
                          f"upload_time, beacon_mac) " \
                          f"VALUES('{episode.title}', " \
                          f"'{episode.content}', " \
                          f"'{episode.uploader_gmail_id}'," \
                          f"'{episode.upload_time}', " \
                          f"'{episode.beacon_mac}'); "
                    cursor.execute(sql)
                    db.commit()
                    episode_id = int(cursor.lastrowid)
                    return episode_id, True
            except Exception as e:
                print(f"error : {e}")
                return -1, False

    def find_episodes_nearby_beacon(self, beacon_mac: str):
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT * FROM episode " \
                          f"WHERE beacon_mac = '{beacon_mac}';"
                    cursor.execute(sql)
                    raw_data_list = cursor.fetchall()
                    return [self.__convert_raw_db_data_to_episode_instance(raw_data)
                            for raw_data in raw_data_list]
            except Exception as e:
                print(f"error : {e}")
                return None

    def find_user_episodes(self, gmail_id: str):
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT * FROM episode " \
                          f"WHERE uploader_gmail_id = '{gmail_id}';"
                    cursor.execute(sql)
                    raw_data_list = cursor.fetchall()
                    return [self.__convert_raw_db_data_to_episode_instance(raw_data)
                            for raw_data in raw_data_list]
            except Exception as e:
                print(f"error : {e}")
                return None


handler_episode_db = HandlerEpisodeDB(handler_db)
