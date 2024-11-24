# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/4
Last Modified: 2023/12/4
Description: 
"""
import json
import datetime

from flask import request
from flask_restx import Resource, Namespace, fields
from bson import ObjectId

from app.extentions import mongo
from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from utils.dt import DateTime
from utils.log import RequestLogUtil


wx_auth_api = Namespace("app", description="移动端API", path="/app_api/v1/auth")


wx_auth_model = wx_auth_api.model('WXLoginModel', {
    'phone_number': fields.String(required=True, description='手机号'),
    'password': fields.String(required=True, description='密码')
})


@wx_auth_api.route('/login')
class WXLoginAPI(Resource):
    @wx_auth_api.doc(description='登录\n目前仅支持账号密码登录', body=wx_auth_model)
    def post(self):
        data = json.loads(request.data)
        phone_number = data.get("phone_number")
        password = data.get("password")

        # 检查手机号是否存在
        user = mongo.db.user.find_one({"phone_number": phone_number})
        if not user:
            return ResponseMaker.not_exist("手机号", {"手机号": phone_number})

        # 检查密码正确性
        if user.get('password') != password:
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

        # 生成token
        user_id = str(user.get("_id"))
        access_token_data = JWTUtil.create_token(user_id)
        access_token = access_token_data.get("access_token")

        token = "Bearer " + access_token

        return ResponseMaker.success(data=token)


@wx_auth_api.route('/logout')
class WXLogoutAPI(Resource):
    @wx_auth_api.doc(description='登出')
    def post(self):
        return ResponseMaker.success()
