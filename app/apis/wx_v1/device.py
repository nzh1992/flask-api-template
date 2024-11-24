# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/5
Last Modified: 2023/12/5
Description: 设备管理API
"""
from flask import request
from flask_restx import Resource, Namespace

from utils.response import ResponseMaker
from utils.jwt import JWTUtil


wx_device_api = Namespace("app", description="移动端API", path="/app_api/v1/device")


@wx_device_api.route('/')
class WXDeviceAPI(Resource):
    @wx_device_api.doc(description='获取设备列表')
    @JWTUtil.verify_token_decorator(request)
    def get(self, *args, **kwargs):
        resp_data = []

        return ResponseMaker.success(resp_data)
