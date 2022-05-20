from typing import List, Dict

from handler.handler_beacon_db import BeaconDBHandler
from handler.handler_db import HandlerDB
from handler.handler_user_db import UserDBHandler
from s3.s3_connect import S3
from utility.utilities import JsonMaker
from model.user import User
import json
from enum import Enum, auto

from model.user_device import UserDevice
from handler.handler_map_db import MapDBHandler
from model.gps_coordinate import GPSCoordinate

from flask import Flask, request

from s3.s3_config import AWS_S3_BUCKET_NAME

s3_client = S3(AWS_S3_BUCKET_NAME)
s3_client.connect()
sticker_image_num = s3_client.get_file_num('sticker/')

app = Flask(__name__)

db_info: Dict[str, any] = {
    "host": "db-capstone.cbo8gwqsco77.ap-northeast-2.rds.amazonaws.com",
    "port": 3306,
    "user": "dbadmin",
    "passwd": "rootroot22",
    "db_name": "db_capstone",
    "charset": "utf8mb4"
}

handler_db = HandlerDB(**db_info)
handler_user_db = UserDBHandler(handler_db)
handler_map_db = MapDBHandler(handler_db)
handler_beacon_db = BeaconDBHandler(handler_db)


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


class ResponseAboutBeacon(Enum):
    NOT_JSON = auto()
    INVALID_INPUT = auto()
    NOT_AUTHORIZED = auto()


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
    if result == UserDBHandler.AccountDbState.NICKNAME_ALREADY_EXISTED:
        return str_to_json(ResponseAboutUser.NICKNAME_ALREADY_USED.name)
    elif result == UserDBHandler.AccountDbState.GMAIL_ID_ALREADY_EXISTED:
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
                                          "longitude"]):
        return str_to_json(ResponseAboutBuilding.INVALID_INPUT.name)
    list_nearby_building = handler_map_db.get_list_nearby_building(
        GPSCoordinate(
            float(params.get("latitude")),
            float(params.get("longitude")))
    )

    result = json.dumps({
        index: {
            "id": building.id,
            "name": building.name,
            "latitude": building.location.coordinate[0],
            "longitude": building.location.coordinate[1]
        } for index, building in enumerate(list_nearby_building)}, ensure_ascii=False)
    return result


@app.route("/get_all_nearby_authorized_beacons", methods=["POST"])
def get_all_nearby_authorized_beacons():
    if not request.is_json:
        return str_to_json(ResponseAboutBeacon.NOT_JSON.name)
    params: Dict[str, str] = request.get_json()
    list_beacon = [params[str(index)] for index in range(len(params))]
    list_beacon = [beacon.get("mac_addr")
                   for beacon in list_beacon]
    try:
        building_id = handler_beacon_db.get_building_id(list_beacon)
        list_beacon_in_building = handler_beacon_db.get_all_beacon_in_building(building_id)
        result = json.dumps({
            index: {
                "mac_addr": beacon.mac_addr,
                "building_id": beacon.building_id,
                "detail_location": beacon.detail_location,
                "popular_user_gmail_id": beacon.popular_user_gmail_id
            } for index, beacon in enumerate(list_beacon_in_building)}, ensure_ascii=False)
        return result
    except Exception as e:
        return str_to_json(ResponseAboutBeacon.NOT_AUTHORIZED.name)


@app.route('/sticker_upload', methods=['POST'])
def upload():
    f = request.files['file']
    params: Dict[str, str] = request.get_json()
    if not does_params_have_keys(params, ["nickname"]):
        return JsonMaker().push('result', {'upload_result': 'nickname not existed'})
    uploader_nick = params.get('uploader_nick')
    time = round(time.time())
    ext = f.filename.split('.')[-1]
    filename = imgname_maker.run(ext)
    local_path = f'./images/{filename}'
    remote_path = f'sticker/{filename}'
    print(local_path)
    f.save(local_path)
    rc = s3_client.upload(local_path, remote_path)
    if rc:
        return JsonMaker().push('result', {'upload_result': 'success'}).json()
    else:
        return JsonMaker().push('result', {'upload_result': 'failure'}).json()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)