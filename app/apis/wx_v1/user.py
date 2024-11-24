# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/4
Last Modified: 2023/12/4
Description: 
"""
from flask import request
from flask_restx import Resource, Namespace

from app.extentions import mongo
from utils.response import ResponseMaker
from utils.jwt import JWTUtil


wx_user_api = Namespace("app", description="移动端API", path="/app_api/v1/user")


@wx_user_api.route('/me')
class WxUserAPI(Resource):
    @wx_user_api.doc(description='查看用户自己信息')
    @JWTUtil.verify_token_decorator(request)
    def get(self, params, *args, **kwargs):
        user_id = request.user.get("_id")
        condition = {"_id": user_id}

        user = mongo.db.user.find_one(condition)
        if not user:
            return ResponseMaker.not_exist("用户", {"id": request.view_args.get("id")})

        user_data = {
            "id": str(user.get("_id")),
            "user_name": user.get("user_name"),
            "phone_number": user.get("phone_number"),
            "role": user.get("role")
        }

        return ResponseMaker.success(user_data)
