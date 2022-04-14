from flask import Flask, render_template, request
from typing import List, Dict
from handler_db import HandlerDb
from handler_user_db import HandlerUserDb
from model.user import User
import json
from enum import Enum, auto

from model.user_device import UserDevice
from handler_map_db import HandlerMapDb
from model.gps_coordinate import GPSCoordinate

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
handler_map_db = HandlerMapDb(handler_db)


class Response(Enum):
    NOT_JSON = auto()
    INVALID_INPUT = auto()


class ResponseAboutUser(Enum):
    NOT_JSON = auto()
    INVALID_INPUT = auto()
    LOGIN_SUCCESS = auto()
    LOGOUT_SUCCESS = auto()
    SIGNUP_SUCCESS = auto()
    ALREADY_LOGGED_IN = auto()
    ALREADY_LOGGED_OUT = auto()
    ACCOUNT_NOT_EXISTED = auto()
    NICKNAME_ALREADY_USED = auto()
    GMAIL_ID_ALREADY_EXISTED = auto()
    NICKNAME_VALID = auto()


class ResponseAboutBuilding(Enum):
    NOT_JSON = auto()
    INVALID_INPUT = auto()


def does_params_have_keys(params: Dict[str, str], keys: List[str]):
    if len(set(keys).difference(set(params.keys()))) == 0:
        return True
    else:
        return False


def str_to_json(value: str):
    return json.dumps({"result": value})


@app.route("/")
def home():
    return str_to_json("Hello, World")


@app.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return str_to_json(ResponseAboutUser.NOT_JSON.name)
    params: Dict[str, str] = request.get_json()
    if not does_params_have_keys(params, ["user_gmail_id", "android_id", "device_model"]):
        return str_to_json(ResponseAboutUser.INVALID_INPUT.name)
    gmail_id = params.get("user_gmail_id")
    current_device = UserDevice(
        params.get("android_id"),
        params.get("device_model")
    )
    if not handler_user_db.is_account_existed(gmail_id):
        return str_to_json(ResponseAboutUser.ACCOUNT_NOT_EXISTED.name)
    if not handler_user_db.is_user_logged_in(gmail_id):
        handler_user_db.login(gmail_id, current_device)
        return str_to_json(ResponseAboutUser.LOGIN_SUCCESS.name)
    else:
        return str_to_json(ResponseAboutUser.ALREADY_LOGGED_IN.name)


@app.route("/logout", methods=["POST"])
def logout():
    if not request.is_json:
        return str_to_json(ResponseAboutUser.NOT_JSON.name)
    params: Dict[str, str] = request.get_json()
    if not does_params_have_keys(params, ["gmail_id"]):
        return str_to_json(ResponseAboutUser.INVALID_INPUT.name)
    gmail_id = params.get("gmail_id")
    if not handler_user_db.is_account_existed(gmail_id):
        return str_to_json(ResponseAboutUser.ACCOUNT_NOT_EXISTED.name)
    if handler_user_db.is_user_logged_in(gmail_id):
        handler_user_db.logout(gmail_id)
        return str_to_json(ResponseAboutUser.LOGOUT_SUCCESS.name)
    else:
        return str_to_json(ResponseAboutUser.ALREADY_LOGGED_OUT.name)


@app.route("/signup", methods=["POST"])
def signup():
    if not request.is_json:
        return str_to_json(ResponseAboutUser.NOT_JSON.name)
    params: Dict[str, str] = request.get_json()
    if not does_params_have_keys(params, ["nickname", "gmail_id", "birthday", "identity"]):
        return str_to_json(ResponseAboutUser.INVALID_INPUT.name)
    user = User(params.get("nickname"),
                params.get("gmail_id"),
                params.get("birthday"),
                params.get("identity"),
                1)
    result = handler_user_db.signup(user)
    if result == HandlerUserDb.AccountDbState.NICKNAME_ALREADY_EXISTED:
        return str_to_json(ResponseAboutUser.NICKNAME_ALREADY_USED.name)
    elif result == HandlerUserDb.AccountDbState.GMAIL_ID_ALREADY_EXISTED:
        return str_to_json(ResponseAboutUser.GMAIL_ID_ALREADY_EXISTED.name)
    else:
        return str_to_json(ResponseAboutUser.SIGNUP_SUCCESS.name)


@app.route("/check_nickname", methods=["POST"])
def check_nickname_duplicate():
    if not request.is_json:
        return str_to_json(ResponseAboutUser.NOT_JSON.name)
    params: Dict[str, str] = request.get_json()
    if not does_params_have_keys(params, ["nickname"]):
        return str_to_json(ResponseAboutUser.INVALID_INPUT.name)
    if handler_user_db.is_nickname_existed(params.get("nickname")):
        return str_to_json(ResponseAboutUser.NICKNAME_ALREADY_USED.name)
    else:
        return str_to_json(ResponseAboutUser.NICKNAME_VALID.name)


@app.route("/nearby_building", methods=["POST"])
def nearby_building():
    if not request.is_json:
        return str_to_json(ResponseAboutBuilding.NOT_JSON.name)
    params: Dict[str, str] = request.get_json()
    if not does_params_have_keys(params, ["latitude",
                                          "longitude",
                                          "range_radius"]):
        return str_to_json(ResponseAboutBuilding.INVALID_INPUT.name)
    list_nearby_building = handler_map_db.get_list_nearby_building(
        GPSCoordinate(
            float(params.get("latitude")),
            float(params.get("longitude"))),
        float(params.get("range_radius"))
    )
    print(list_nearby_building[0].name)

    result = json.dumps({
        index: {
            "id": building.id,
            "name": building.name,
            "latitude": building.location.coordinate[0],
            "longitude": building.location.coordinate[1]
        } for index, building in enumerate(list_nearby_building)}, ensure_ascii=False)
    return result


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
