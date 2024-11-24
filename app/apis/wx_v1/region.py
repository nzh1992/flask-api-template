# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/13
Last Modified: 2023/12/13
Description: 
"""
import os
import json

from flask import request
from flask_restx import Resource, Namespace

from utils.response import ResponseMaker
from utils.jwt import JWTUtil


wx_region_api = Namespace("app", description="移动端API", path="/app_api/v1/region")


@wx_region_api.route('/')
class WXRegionAPI(Resource):
    @wx_region_api.doc(description='获取所有省市区')
    @JWTUtil.verify_token_decorator(request)
    def get(self, *args, **kwargs):
        print(os.getcwd())
        # 省市区文件路径
        region_fp = os.path.join(os.getcwd(), "data", "最新县及县以上行政区划代码.txt")

        with open(region_fp, 'r') as f:
            f_data = f.read()
            region_data = json.loads(f_data)

        return ResponseMaker.success(region_data)