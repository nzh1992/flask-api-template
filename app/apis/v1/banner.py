# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/29
Last Modified: 2023/11/29
Description: 微信小程序，banner
"""
from flask import request
from flask_restx import Resource, Namespace, fields

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from app.models.banner import Banner
from utils.log import RequestLogUtil


banner_api = Namespace("client", description="客户端API", path="/api/v1/weapp/banner")


banner_item_model = banner_api.model('BannerItemModel', {
    'id': fields.String(required=False, description=''),
    'url': fields.String(required=False, description='')
})


banner_model = banner_api.model("BannerModel", {
    'autoplay': fields.Boolean(required=True, description='是否自动播放'),
    'interval': fields.Float(required=True, description='是否自动播放'),
    'banner_list': fields.List(fields.Nested(banner_item_model), required=False, description='是否自动播放'),
})


@banner_api.route('/')
class BannerAPI(Resource):
    @banner_api.doc(description='修改小程序banner配置', body=banner_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def patch(self, *args, **kwargs):
        data = request.get_json(force=True)
        Banner(req=request).update(data)
        return ResponseMaker.success()

    @banner_api.doc(description='获取小程序banner配置')
    @JWTUtil.verify_token_decorator(request)
    def get(self, *args, **kwargs):
        banner = Banner(req=request).get()

        banner_data = {
            "autoplay": banner.get("autoplay"),
            "interval": banner.get("interval"),
            "banner_list": banner.get("banner_list")
        }

        return ResponseMaker.success(banner_data)