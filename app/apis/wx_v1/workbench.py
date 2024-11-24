# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/30
Last Modified: 2023/11/30
Description: 工作台
"""
from flask import request
from flask_restx import Resource, Namespace

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from app.models.land import Land
from app.models.banner import Banner


wx_workbench_api = Namespace("app", description="移动端API", path="/app_api/v1/workbench")


@wx_workbench_api.route('/')
class WXWorkbenchAPI(Resource):
    @wx_workbench_api.doc(description='获取工作台数据')
    @JWTUtil.verify_token_decorator(request)
    def get(self, *args, **kwargs):
        # 土地汇总
        land_data_list = Land(req=request).get_all_of_location()

        # 小程序banner
        banner = Banner(req=request).get()
        banner_data = {
            "autoplay": banner.get("autoplay"),
            "interval": banner.get("interval"),
            "banner_list": [l.get("url") for l in banner.get("banner_list")]
        }

        resp_data = {
            "land_list": land_data_list,
            "banner": banner_data
        }

        return ResponseMaker.success(resp_data)

