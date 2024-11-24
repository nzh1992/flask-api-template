# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/19
Last Modified: 2023/11/19
Description:
"""
import datetime
import json

from flask import request
from flask_restx import Resource, Namespace, fields
from werkzeug.security import check_password_hash
from bson import ObjectId

from app.extentions import mongo
from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from utils.dt import DateTime


auth_api = Namespace("client", description="客户端API", path="/client_api/v1/auth")


auth_model = auth_api.model('LoginModel', {
    'phone_number': fields.String(required=True, description='手机号'),
    'password': fields.String(required=True, description='密码')
})


@auth_api.route('/login')
class UserAPI(Resource):
    @auth_api.doc(description='登录\n目前仅支持手机号密码登录', body=auth_model)
    def post(self):
        data = json.loads(request.data)
        phone_number = data.get("phone_number")
        password = data.get("password")

        # 检查账号是否存在
        user = mongo.db.user.find_one({"phone_number": phone_number})
        if not user:
            return ResponseMaker.not_exist("用户", {"手机号": phone_number})

        # 检查密码正确性
        if password != user.get("password"):
            return ResponseMaker.user_password_error()

        # 检查企业状态
        enterprise_id = user.get("enterprise_id")
        enterprise = mongo.db.enterprise.find_one({"_id": ObjectId(enterprise_id)})
        if enterprise.get("status") == "DISABLE":
            return ResponseMaker.login_enterprise_disable()

        # 检查账号所在企业是否在授权周期内
        current_dt = DateTime.get_datetime_now()
        start_dt = datetime.datetime.strptime(enterprise.get("start_date"), "%Y-%m-%d")
        end_dt = datetime.datetime.strptime(enterprise.get("end_date"), "%Y-%m-%d")
        if current_dt < start_dt or current_dt > end_dt:
            return ResponseMaker.login_enterprise_deprecated()

        # 只有管理员才能登录客户端
        if user.get("role") != "ADMIN":
            return ResponseMaker.not_admin()

        # 生成token
        user_id = str(user.get("_id"))
        access_token_data = JWTUtil.create_token(user_id)
        access_token = access_token_data.get("access_token")
        token_expires = access_token_data.get("token_expires")

        resp_data = {
            'token': "Bearer " + access_token,
            'user_id': user_id,
            'user_name': user.get("user_name")
        }

        return ResponseMaker.success(data=resp_data)


@auth_api.route('/logout')
class UserAPI(Resource):
    @auth_api.doc(description='登出')
    def post(self):
        return ResponseMaker.success()
