from src.handler_db import HandlerDb


class HandlerMap:
    def __init__(self, handler_db: HandlerDb):
        self.__handler_db = handler_db

    def __connect_db(self):
        return self.__handler_db.connect_db()

    # 1km 이내에 있는 건물들의 리스트를 반환
    def get_list_nearby_building(self, user_cur_location:) -> bool:
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT is_active FROM user WHERE gmail_id = '{gmail_id}'"
                    cursor.execute(sql)
                    is_active = cursor.fetchone()[0]
                    return is_active != 0
            except Exception as e:
                print(f"error : {e}")
                return False
