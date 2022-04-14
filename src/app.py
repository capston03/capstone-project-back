import sys

from flask import Flask, render_template, request
from typing import List, Dict
from handler_db import HandlerDb
from handler_user_db import HandlerUserDb
from model.user import User
import json

from src.model.user_device import UserDevice

app = Flask(__name__)

db_info: Dict[str, any] = {
    "host": "db-capstone.cbo8gwqsco77.ap-northeast-2.rds.amazonaws.com",
    "port": 3306,
    "user": "dbadmin",
    "passwd": "rootroot22",
    "db_name": "db_capstone",
    "charset": "utf8mb4"
}

handler_db = HandlerDb(**db_info)
handler_user_db = HandlerUserDb(handler_db)


def str_to_json(value: str) -> str:
    return json.dumps({"result": value})


@app.route("/")
def home():
    return "Hello, World"


@app.route("/beacon")
def show_beacons():
    list_beacon = handler_db.get_all("beacon")
    return str(list_beacon)


@app.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return str_to_json("NOT_JSON")
    params: Dict[str, str] = request.get_json()
    gmail_id = params.get("user_gmail_id")
    current_device = UserDevice(
        params.get("android_id"),
        params.get("device_model")
    )
    is_account_existed = handler_user_db.is_account_existed(gmail_id)
    if not is_account_existed:
        return str_to_json("USER_ACCOUNT_IS_NOT_EXISTED")
    is_user_active = handler_user_db.is_user_already_logged_in(gmail_id)
    can_login = is_account_existed and not is_user_active
    if can_login:
        handler_user_db.login(gmail_id, current_device)
        return str_to_json("LOGIN_SUCCESS")
    else:
        return str_to_json("USER_IS_ALREADY_LOGGED_IN")


@app.route("/logout", methods=["POST"])
def logout():
    if not request.is_json:
        return str_to_json("NOT_JSON")
    params: Dict[str, str] = request.get_json()
    gmail_id = params.get("user_gmail_id")
    is_account_existed = handler_user_db.is_account_existed(gmail_id)
    if not is_account_existed:
        return str_to_json("USER_ACCOUNT_IS_NOT_EXISTED")
    is_user_active = handler_user_db.is_user_already_logged_in(gmail_id)
    can_logout = is_account_existed and is_user_active
    if can_logout:
        handler_user_db.logout(gmail_id)
        return str_to_json("LOGOUT_SUCCESS")
    else:
        return str_to_json("USER_IS_ALREADY_LOGGED_OUT")


@app.route("/signup", methods=["POST"])
def signup():
    if not request.is_json:
        return str_to_json("NOT_JSON")
    params: Dict[str, str] = request.get_json()
    if "nickname" not in params \
            or "gmail_id" not in params \
            or "birthday" not in params \
            or "identity" not in params:
        return str_to_json("NOT_VALID_USER_INFO")
    user = User(params.get("nickname"),
                params.get("gmail_id"),
                params.get("birthday"),
                params.get("identity"),
                1)
    result = handler_user_db.signup(user)
    if result == HandlerUserDb.DbState.NICKNAME_ALREADY_EXISTED:
        return str_to_json("NICKNAME_IS_ALREADY_USED")
    elif result == HandlerUserDb.DbState.ACCOUNT_ALREADY_EXISTED:
        return str_to_json("ACCOUNT_IS_ALREADY_EXISTED")
    else:
        return str_to_json("SIGNUP_SUCCESS")


@app.route("/check_nickname", methods=["POST"])
def check_nickname_duplicate():
    if not request.is_json:
        return str_to_json("NOT_JSON")
    params: Dict[str, str] = request.get_json()
    if "nickname" not in params:
        return str_to_json("NOT_VALID_USER_INFO")
    is_nickname_duplicate = handler_user_db.is_nickname_existed(params.get("nickname"))
    if is_nickname_duplicate:
        return str_to_json("EXISTED")
    else:
        return str_to_json("NOT_EXISTED")


@app.route("/users")
def show_all_user():
    list_user = handler_db.get_all("user")
    return str_to_json(str(list_user))


@app.route("/board")
def boards():
    list_board = handler_db.get_all("board")
    return str_to_json(str(list_board))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
