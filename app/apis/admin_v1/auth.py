# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/19
Last Modified: 2023/11/19
Description:
"""
import json

from flask import request
from flask_restx import Resource, Namespace, fields
from werkzeug.security import check_password_hash

from app.extentions import mongo
from utils.response import ResponseMaker
from utils.jwt import JWTUtil


admin_auth_api = Namespace("admin", description="管理端API", path="/admin_api/v1/auth")

auth_model = admin_auth_api.model('AdminLoginModel', {
    'phone_number': fields.String(required=True, description='手机号'),
    'password': fields.String(required=True, description='密码')
})


@admin_auth_api.route('/login')
class UserLoginAPI(Resource):
    @admin_auth_api.doc(description='登录', body=auth_model)
    def post(self):
        data = json.loads(request.data)
        phone_number = data.get("phone_number")
        password = data.get("password")

        # 检查账号是否存在
        user = mongo.db.admin_user.find_one({"phone_number": phone_number})
        if not user:
            return ResponseMaker.not_exist("用户", {"手机号": phone_number})

        # 检查密码正确性
        if user.get('password') != password:
            return ResponseMaker.user_password_error()

        # 生成token
        user_id = str(user.get("_id"))
        access_token_data = JWTUtil.create_token(user_id)
        access_token = access_token_data.get("access_token")

        resp_data = {
            'token': "Bearer " + access_token,
            'user_id': user_id,
            'user_name': user.get("user_name"),
        }

        return ResponseMaker.success(data=resp_data)


@admin_auth_api.route('/logout')
class UserLogoutAPI(Resource):
    @admin_auth_api.doc(description='登出')
    def post(self):
        return ResponseMaker.success()
