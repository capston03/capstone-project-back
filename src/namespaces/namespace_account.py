from flask import request
from flask_restx import Resource, Namespace

from handler.handler_user_db import UserDBHandler
from model.user import User
from model.user_device import UserDevice
from utility.utilities import *
from handler.handler_user_db import handler_user_db as user_db_handler

namespace_account = Namespace('account', 'Api for account')


@namespace_account.route('/login')
class Login(Resource):
    def post(self):
        if not request.is_json:
            return to_json({"code": "not_json"})
        params: Dict[str, str] = request.get_json()
        if not check_if_param_has_keys(params, ["user_gmail_id", "android_id", "device_model"]):
            return to_json({"code": "invalid_input"})
        gmail_id = params.get("user_gmail_id")
        current_device = UserDevice(
            params.get("android_id"),
            params.get("device_model")
        )
        if not user_db_handler.is_account_existed(gmail_id):
            return to_json({"code": "account_not_existed"})
        if not user_db_handler.is_user_logged_in(gmail_id):
            user_db_handler.login(gmail_id, current_device)
            nickname = user_db_handler.get_nickname(gmail_id)
            return to_json({"code": "success", "nickname": nickname})
        else:
            return to_json({"code": "already_logged_in"})


@namespace_account.route('/logout')
class Logout(Resource):
    def post(self):
        if not request.is_json:
            return to_json('not_json')
        params: Dict[str, str] = request.get_json()
        if not check_if_param_has_keys(params, ["gmail_id"]):
            return to_json('invalid_input')
        gmail_id = params.get("gmail_id")
        if not user_db_handler.is_account_existed(gmail_id):
            return to_json('account_not_existed')
        if user_db_handler.is_user_logged_in(gmail_id):
            user_db_handler.logout(gmail_id)
            return to_json('success')
        else:
            return to_json('already_logged_out')


@namespace_account.route('/signup')
class Signup(Resource):
    def post(self):
        if not request.is_json:
            return to_json('not_json')
        params: Dict[str, str] = request.get_json()
        if not check_if_param_has_keys(params, ["nickname", "gmail_id", "birthday", "identity"]):
            return to_json('invalid_input')
        user = User(params.get("nickname"),
                    params.get("gmail_id"),
                    params.get("birthday"),
                    params.get("identity"),
                    1)
        result = user_db_handler.signup(user)
        if result == UserDBHandler.Result.NICKNAME_ALREADY_EXISTED:
            return to_json('nickname_already_used')
        elif result == UserDBHandler.Result.GMAIL_ID_ALREADY_EXISTED:
            return to_json('gmail_id_already_used')
        else:
            return to_json('success')


@namespace_account.route('/check_nickname')
class CheckNickname(Resource):
    def post(self):
        if not request.is_json:
            return to_json('not_json')
        params: Dict[str, str] = request.get_json()
        if not check_if_param_has_keys(params, ["nickname"]):
            return to_json('invalid_input')
        if user_db_handler.is_nickname_existed(params.get("nickname")):
            return to_json('already_used')
        else:
            return to_json('valid')
