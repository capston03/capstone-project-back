from flask import request
from flask_restx import Resource, Namespace

from handler.user_DB_handler import UserDBHandler
from model.user import User
from model.user_device import UserDevice
from utility.utilities import *
from handler.user_DB_handler import user_DB_handler

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
        try:
            if not user_DB_handler.is_account_existed(gmail_id):
                return to_json({"code": "account_not_existed"})
            if not user_DB_handler.is_user_logged_in(gmail_id):
                user_DB_handler.login(gmail_id, current_device)
                nickname = user_DB_handler.get_nickname(gmail_id)
                return to_json({"code": "success", "nickname": nickname})
            else:
                return to_json({"code": "already_logged_in"})
        except Exception as e:
            print(str(e))
            return to_json({"code": "error"})


@namespace_account.route('/logout')
class Logout(Resource):
    def post(self):
        if not request.is_json:
            return to_json('not_json')
        params: Dict[str, str] = request.get_json()
        if not check_if_param_has_keys(params, ["gmail_id"]):
            return to_json('invalid_input')
        gmail_id = params.get("gmail_id")
        try:
            if not user_DB_handler.is_account_existed(gmail_id):
                return to_json('account_not_existed')
            if user_DB_handler.is_user_logged_in(gmail_id):
                user_DB_handler.logout(gmail_id)
                return to_json('success')
            else:
                return to_json('already_logged_out')
        except Exception as e:
            print(str(e))
            return to_json("error")


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
        try:
            result = user_DB_handler.signup(user)
            if result == UserDBHandler.Result.NICKNAME_ALREADY_EXISTED:
                return to_json('nickname_already_used')
            elif result == UserDBHandler.Result.GMAIL_ID_ALREADY_EXISTED:
                return to_json('gmail_id_already_used')
            else:
                return to_json('success')
        except Exception as e:
            print(str(e))
            return to_json("error")


@namespace_account.route('/check_nickname')
class CheckNickname(Resource):
    def post(self):
        if not request.is_json:
            return to_json('not_json')
        params: Dict[str, str] = request.get_json()
        if not check_if_param_has_keys(params, ["nickname"]):
            return to_json('invalid_input')
        try:
            if user_DB_handler.is_nickname_existed(params.get("nickname")):
                return to_json('already_used')
            else:
                return to_json('valid')
        except Exception as e:
            print(str(e))
            return to_json("error")
