import sys

from flask import Flask, render_template, request
from typing import List, Dict
from handler_db import HandlerDb
from handler_user_db import HandlerUserDb
from model.user import User
import json

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
        return str_to_json("NOT JSON")
    params: Dict[str, str] = request.get_json()
    gmail_id = params.get("gmail_id")
    is_account_existed = handler_user_db.is_account_existed(gmail_id)
    if not is_account_existed:
        return str_to_json("USER ACCOUNT IS NOT EXISTED")
    is_user_active = handler_user_db.is_user_already_logged_in(gmail_id)
    can_login = is_account_existed and not is_user_active
    if can_login:
        handler_user_db.login(gmail_id)
        return str_to_json("LOGIN SUCCESS")
    else:
        return str_to_json("USER IS ALREADY LOGGED IN")


@app.route("/logout", methods=["POST"])
def logout():
    if not request.is_json:
        return str_to_json("NOT JSON")
    params: Dict[str, str] = request.get_json()
    gmail_id = params.get("gmail_id")
    is_account_existed = handler_user_db.is_account_existed(gmail_id)
    if not is_account_existed:
        return str_to_json("USER ACCOUNT IS NOT EXISTED")
    is_user_active = handler_user_db.is_user_already_logged_in(gmail_id)
    can_logout = is_account_existed and is_user_active
    if can_logout:
        handler_user_db.logout(gmail_id)
        return str_to_json("LOGOUT SUCCESS")
    else:
        return str_to_json("USER IS ALREADY LOGGED OUT")


@app.route("/signup", methods=["POST"])
def signup():
    if not request.is_json:
        return str_to_json("NOT JSON")
    params: Dict[str, str] = request.get_json()
    if "nickname" not in params \
            or "gmail_id" not in params \
            or "birthday" not in params \
            or "identity" not in params:
        return str_to_json("NOT VALID USER INFO")
    user = User(params.get("nickname"),
                params.get("gmail_id"),
                params.get("birthday"),
                params.get("identity"),
                1)
    result = handler_user_db.signup(user)
    if result == HandlerUserDb.DbState.NICKNAME_ALREADY_EXISTED:
        return str_to_json("NICKNAME IS ALREADY USED")
    elif result == HandlerUserDb.DbState.ACCOUNT_ALREADY_EXISTED:
        return str_to_json("ACCOUNT IS ALREADY EXISTED")
    else:
        return str_to_json("SIGNUP SUCCESS")


@app.route("/check_nickname", methods=["POST"])
def check_nickname_duplicate():
    if not request.is_json:
        return str_to_json("NOT JSON")
    params: Dict[str, str] = request.get_json()
    if "nickname" not in params:
        return str_to_json("NOT VALID USER INFO")
    is_nickname_duplicate = handler_user_db.is_nickname_existed(params.get("nickname"))
    if is_nickname_duplicate:
        return str_to_json("EXISTED")
    else:
        return str_to_json("NOT EXISTED")


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
