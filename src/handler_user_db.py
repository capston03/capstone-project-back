import pymysql

from handler_db import HandlerDb
from model.user import User
from enum import Enum
from enum import auto


class HandlerUserDb:
    class DbState(Enum):
        NICKNAME_ALREADY_EXISTED = auto()
        ACCOUNT_ALREADY_EXISTED = auto()
        UNKNOWN_ERROR = auto()
        OK = auto()

    def __init__(self, handler_db: HandlerDb):
        self.__handler_db = handler_db

    def __connect_db(self):
        return self.__handler_db.connect_db()

    # Check whether the user account is already existed
    def is_account_existed(self, gmail_id: str) -> bool:
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT EXISTS(SELECT * FROM user WHERE gmail_id = '{gmail_id}' LIMIT 1) AS SUCCESS"
                    cursor.execute(sql)
                    result = cursor.fetchone()
                    return result[0] == 1
            except Exception as e:
                print(f"error : {e}")
                return False

    # Check whether the user is already logged in
    def is_user_already_logged_in(self, gmail_id: str) -> bool:
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

    # Login
    def login(self, gmail_id: str):
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"UPDATE user SET is_active = 1 WHERE gmail_id = '{gmail_id}'"
                    cursor.execute(sql)
                    db.commit()
                    return True
            except Exception as e:
                print(f"error : {e}")
                return False

    # Logout
    def logout(self, gmail_id: str):
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"UPDATE user SET is_active = 0 WHERE gmail_id = '{gmail_id}'"
                    cursor.execute(sql)
                    db.commit()
                    return True
            except Exception as e:
                print(f"error : {e}")
                return False

    # Check whether nickname is existed in the database
    def is_nickname_existed(self, nickname: str) -> bool:
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT EXISTS(SELECT * FROM user WHERE nickname = '{nickname}' LIMIT 1) AS SUCCESS"
                    cursor.execute(sql)
                    result = cursor.fetchone()
                    return result[0] == 1
            except Exception as e:
                print(f"error : {e}")
                return False

    def signup(self, user: User) -> DbState:
        if self.is_nickname_existed(user.nickname):
            return HandlerUserDb.DbState.NICKNAME_ALREADY_EXISTED
        elif self.is_account_existed(user.gmail_id):
            return HandlerUserDb.DbState.ACCOUNT_ALREADY_EXISTED
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"INSERT INTO user (nickname, gmail_id, birthday, identity, is_active) " \
                          f"VALUES('{user.nickname}', " \
                          f"'{user.gmail_id}', " \
                          f"'{user.birthday.to_string()}', " \
                          f"'{user.identity}', " \
                          f"'{user.is_active}')"
                    cursor.execute(sql)
                    db.commit()
                    return HandlerUserDb.DbState.OK
            except Exception as e:
                print(f"error : {e}")
                return HandlerUserDb.DbState.UNKNOWN_ERROR
