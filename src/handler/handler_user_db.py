from model.user import User
from enum import Enum
from enum import auto
from typing import List, Final
import datetime

from model.user_device import UserDevice
from .handler_db import handler_db, HandlerDB


# Handler for user DB
class UserDBHandler:
    LIST_ANDROID_ID_LEN: Final[int] = 5

    class Result(Enum):
        UNKNOWN_ERR = auto()
        OK = auto()
        FULL = auto()
        NEED_TO_ADD = auto()
        EXISTED = auto()
        GMAIL_ID_ALREADY_EXISTED = auto()
        NICKNAME_ALREADY_EXISTED = auto()

    def __init__(self, handler_db: HandlerDB):
        self.__handler_db = handler_db

    def __connect_db(self):
        """
        Connect to the database (AWS RDS).
        :return: Connection
        """
        return self.__handler_db.connect_db()

    def is_account_existed(self, gmail_id: str) -> bool:
        """
        Check whether the user account is already existed.
        :param gmail_id: Gmail id
        :return: Check result
        """
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

    def is_user_logged_in(self, gmail_id: str) -> bool:
        """
        Check whether the user is already logged in.
        :param gmail_id: Gmail id
        :return: Check result
        """
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

    def login(self, gmail_id, current_device: UserDevice):
        """
        Login
        :param gmail_id: User's gmail id
        :param current_device: User's current device
        :return: Whether the user can login
        """
        result = self.__can_access_with_current_device(gmail_id, current_device)
        if result == UserDBHandler.Result.FULL:
            self.__delete_last_device(gmail_id)
            self.__add_current_device(gmail_id, current_device)
        elif result == UserDBHandler.Result.NEED_TO_ADD:
            self.__add_current_device(gmail_id, current_device)
        elif result == UserDBHandler.Result.EXISTED:
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

    def logout(self, gmail_id: str):
        """
        Logout
        :param gmail_id: User's gmail id
        :return: Whether the user can logout
        """
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

    def is_nickname_existed(self, nickname: str) -> bool:
        """
        Check whether the nickname is already used one.
        :param nickname: Nickname
        :return: Check result
        """
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

    def signup(self, user: User) -> Result:
        """
        Signup
        :param user: Information about user
        :return: Whether the user can signup (create the account)
        """
        if self.is_nickname_existed(user.nickname):
            return UserDBHandler.Result.NICKNAME_ALREADY_EXISTED
        elif self.is_account_existed(user.gmail_id):
            return UserDBHandler.Result.GMAIL_ID_ALREADY_EXISTED
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
                    return UserDBHandler.Result.OK
            except Exception as e:
                print(f"error : {e}")
                return UserDBHandler.Result.UNKNOWN_ERR

    def __get_list_android_id(self, gmail_id) -> List[str]:
        """
        Get the list of user's device id.
        :param gmail_id: User's gmail id
        :return: List of user's device id
        """
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT * FROM user_device WHERE user_gmail_id = '{gmail_id}';"
                    cursor.execute(sql)
                    list_android_id = [user_device[1] for user_device in cursor.fetchall()]
                    return list_android_id
            except Exception:
                raise

    def __can_access_with_current_device(self, gmail_id: str, current_device: UserDevice) -> Result:
        """
        Check that user can login with this device (current device)
        :param gmail_id: User's gmail id
        :param current_device: User's current device
        :return: Check result
        """
        try:
            list_android_id = self.__get_list_android_id(gmail_id)
        except Exception as e:
            print(f"error : {e}")
            return UserDBHandler.Result.UNKNOWN_ERR
        if current_device.android_id in list_android_id:
            return UserDBHandler.Result.EXISTED
        elif len(list_android_id) == self.LIST_ANDROID_ID_LEN:
            return UserDBHandler.Result.FULL
        else:
            return UserDBHandler.Result.NEED_TO_ADD

    def __add_current_device(self, gmail_id: str, current_device: UserDevice) -> Result:
        """
        Add this device information to the user's device list.
        :param gmail_id: User's gmail id
        :param current_device: Current device
        :return: Whether It can be added
        """
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
                    return UserDBHandler.Result.OK
            except Exception as e:
                print(f"error : {e}")
                return UserDBHandler.Result.UNKNOWN_ERR

    def __delete_last_device(self, gmail_id: str) -> Result:
        """
        Delete the last connected device.
        :param gmail_id: User's gmail id
        :return: Operation result
        """
        try:
            last_android_id = self.__get_list_android_id(gmail_id)[-1]
        except Exception as e:
            print(f"error : {e}")
            return UserDBHandler.Result.UNKNOWN_ERR
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    sql = f"DELETE FROM user_device WHERE android_id = '{last_android_id}';"
                    cursor.execute(sql)
                    db.commit()
                    return UserDBHandler.Result.OK
            except Exception as e:
                print(f"error : {e}")
                return UserDBHandler.Result.UNKNOWN_ERR

    def __update_last_login_date(self, gmail_id: str, current_device: UserDevice) -> Result:
        """
        Update the last login date.
        :param gmail_id: User's gmail id
        :param current_device: Current device
        :return: Operation result
        """
        with self.__connect_db() as db:
            with db.cursor() as cursor:
                try:
                    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    sql = f"UPDATE user_device SET login_date = '{now}' " \
                          f"WHERE user_gmail_id = '{gmail_id}' AND android_id = '{current_device.android_id}'"
                    cursor.execute(sql)
                    db.commit()
                    return UserDBHandler.Result.OK
                except Exception as e:
                    print(f"error : {e}")
                    return UserDBHandler.Result.UNKNOWN_ERR

    def get_nickname(self, gmail_id: str):
        with self.__connect_db() as db:
            try:
                with db.cursor() as cursor:
                    sql = f"SELECT nickname FROM user WHERE gmail_id = '{gmail_id}';"
                    cursor.execute(sql)
                    return cursor.fetchone()[0]
            except Exception:
                raise


handler_user_db = UserDBHandler(handler_db)
