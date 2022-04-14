import pymysql

from handler_db import HandlerDb
from model.user import User
from enum import Enum
from enum import auto
from typing import Dict, List, Final, Union
import datetime

from model.user_device import UserDevice


class HandlerUserDb:
    LIST_ANDROID_ID_LEN: Final[int] = 5

    class UserDeviceDbState(Enum):
        UNKNOWN_ERROR = auto()
        OK = auto()
        FULL = auto()
        NEED_TO_ADD = auto()
        EXISTED = auto()

    class AccountDbState(Enum):
        UNKNOWN_ERROR = auto()
        GMAIL_ID_ALREADY_EXISTED = auto()
        NICKNAME_ALREADY_EXISTED = auto()
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
    def is_user_logged_in(self, gmail_id: str) -> bool:
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
    def login(self, gmail_id, current_device: UserDevice):
        result = self.__can_access_with_current_device(gmail_id, current_device)
        if result == HandlerUserDb.UserDeviceDbState.FULL:
            print("Full")
            self.__delete_last_device(gmail_id)
            self.__add_current_device(gmail_id, current_device)
            print("Add device info")
        elif result == HandlerUserDb.UserDeviceDbState.NEED_TO_ADD:
            print("Add device info")
            self.__add_current_device(gmail_id, current_device)
        elif result == HandlerUserDb.UserDeviceDbState.EXISTED:
            print("Existed")
            self.__update_last_login_date(gmail_id, current_device)
        else:
            return False

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

    def signup(self, user: User) -> AccountDbState:
        if self.is_nickname_existed(user.nickname):
            return HandlerUserDb.AccountDbState.NICKNAME_ALREADY_EXISTED
        elif self.is_account_existed(user.gmail_id):
            return HandlerUserDb.AccountDbState.GMAIL_ID_ALREADY_EXISTED
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
                    return HandlerUserDb.AccountDbState.OK
            except Exception as e:
                print(f"error : {e}")
                return HandlerUserDb.AccountDbState.UNKNOWN_ERROR

    def __get_list_android_id(self, gmail_id) -> List[str]:
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT * FROM user_device WHERE user_gmail_id = '{gmail_id}';"
                    cursor.execute(sql)
                    list_android_id = [user_device[1] for user_device in cursor.fetchall()]
                    return list_android_id
            except Exception:
                raise

    def __can_access_with_current_device(self, gmail_id: str, current_device: UserDevice) -> UserDeviceDbState:
        try:
            list_android_id = self.__get_list_android_id(gmail_id)
        except Exception as e:
            print(f"error : {e}")
            return HandlerUserDb.UserDeviceDbState.UNKNOWN_ERROR
        if current_device.android_id in list_android_id:
            return HandlerUserDb.UserDeviceDbState.EXISTED
        elif len(list_android_id) == self.LIST_ANDROID_ID_LEN:
            return HandlerUserDb.UserDeviceDbState.FULL
        else:
            return HandlerUserDb.UserDeviceDbState.NEED_TO_ADD

    def __add_current_device(self, gmail_id: str, current_device: UserDevice) -> UserDeviceDbState:
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    sql = f"INSERT INTO user_device (user_gmail_id, android_id, device_model, login_date) " \
                          f"VALUES('{gmail_id}', " \
                          f"'{current_device.android_id}', " \
                          f"'{current_device.device_model}', " \
                          f"'{now}');"
                    cursor.execute(sql)
                    db.commit()
                    return HandlerUserDb.UserDeviceDbState.OK
            except Exception as e:
                print(f"error : {e}")
                return HandlerUserDb.UserDeviceDbState.UNKNOWN_ERROR

    def __delete_last_device(self, gmail_id: str) -> UserDeviceDbState:
        try:
            last_android_id = self.__get_list_android_id(gmail_id)[-1]
        except Exception as e:
            print(f"error : {e}")
            return HandlerUserDb.UserDeviceDbState.UNKNOWN_ERROR
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    sql = f"DELETE FROM user_device WHERE android_id = '{last_android_id}';"
                    cursor.execute(sql)
                    db.commit()
                    return HandlerUserDb.UserDeviceDbState.OK
            except Exception as e:
                print(f"error : {e}")
                return HandlerUserDb.UserDeviceDbState.UNKNOWN_ERROR

    def __update_last_login_date(self, gmail_id: str, current_device: UserDevice) -> UserDeviceDbState:
        with self.__connect_db() as db:
            with db.cursor() as cursor:
                try:
                    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    sql = f"UPDATE user_device SET login_date = '{now}' " \
                          f"WHERE user_gmail_id = '{gmail_id}' AND android_id = '{current_device.android_id}'"
                    cursor.execute(sql)
                    db.commit()
                    return HandlerUserDb.UserDeviceDbState.OK
                except Exception as e:
                    print(f"error : {e}")
                    return HandlerUserDb.UserDeviceDbState.UNKNOWN_ERROR
