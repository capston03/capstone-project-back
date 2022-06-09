from model.episode import Episode
from handler.DB_handler import DBHandler, DB_handler
from utility.utilities import make_error_message


class EpisodeDBhandler:

    def __init__(self, _DB_handler: DBHandler):
        self.handler_db = _DB_handler

    def __connect_db(self):
        return self.handler_db.connect()

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
                raise Exception(make_error_message(str(e)))

    def write(self, episode: Episode) -> int:
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
                    return episode_id
            except Exception as e:
                raise Exception(make_error_message(str(e)))

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
                raise Exception(make_error_message(str(e)))

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
                raise Exception(make_error_message(str(e)))


episode_DB_handler = EpisodeDBhandler(DB_handler)
