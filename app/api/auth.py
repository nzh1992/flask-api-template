# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2024/11/24
Last Modified: 2024/11/24
Description: 
"""
import datetime
import json

from flask import request
from flask_restx import Resource, Namespace, fields

from utils.response import ResponseMaker


auth_api = Namespace("auth", description="认证", path="/api/auth")


auth_model = auth_api.model('LoginModel', {
    'account': fields.String(required=True, description='账号'),
    'password': fields.String(required=True, description='密码')
})


@auth_api.route('/login')
class UserAPI(Resource):
    @auth_api.doc(description='登录', body=auth_model)
    def post(self):
        data = json.loads(request.data)
        account = data.get("account")
        password = data.get("password")



        # 生成token
        # user_id = str(user.get("_id"))
        # access_token_data = JWTUtil.create_token(user_id)
        # access_token = access_token_data.get("access_token")
        # token_expires = access_token_data.get("token_expires")
        #
        # resp_data = {
        #     'token': "Bearer " + access_token,
        #     'user_id': user_id,
        #     'user_name': user.get("user_name")
        # }

        return ResponseMaker.success(data={"a": "b"})


@auth_api.route('/logout')
class UserAPI(Resource):
    @auth_api.doc(description='登出')
    def post(self):
        return ResponseMaker.success()
