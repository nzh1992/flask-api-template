# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2024/9/11
Last Modified: 2024/9/11
Description: 
"""
from flask import request
from flask_restx import Resource, Namespace, fields

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from app.models.default_enter import DefaultEnterModel
from utils.log import RequestLogUtil


wx_default_enter_api = Namespace("app", description="客户端API", path="/app_api/v1/default_enter")


@wx_default_enter_api.route('/all')
class DefaultEnterListAPI(Resource):
    @wx_default_enter_api.doc(description='全部预设录入')
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def get(self, *args, **kwargs):
        default_enter_model = DefaultEnterModel(req=request)
        default_enters = default_enter_model.get_all()

        default_enter_list = []

        for default_enter in default_enters:
            default_enter_data = {
                "id": str(default_enter.get("_id")),
                "name": default_enter.get("name"),
            }
            default_enter_list.append(default_enter_data)

        return ResponseMaker.success(default_enter_list)