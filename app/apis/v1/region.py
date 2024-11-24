# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/24
Last Modified: 2023/11/24
Description: 省市区
"""
import os
import json

from flask import request
from flask_restx import Resource, Namespace

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from app.extentions import mongo


region_api = Namespace("client", description="客户端API", path="/client_api/v1/region")


@region_api.route('/list')
class RegionProvinceAPI(Resource):
    @region_api.doc(description='获取所有省市区列表')
    @JWTUtil.verify_token_decorator(request)
    def get(self, *args, **kwargs):
        # 省
        provinces = mongo.db.province.find({})
        province_list = []
        for p in provinces:
            p.pop('_id')
            province_list.append(p)

        # 市
        citys = mongo.db.city.find({})
        city_list = []
        for c in citys:
            c.pop('_id')
            c.pop("parent_code")
            city_list.append(c)

        # 区
        areas = mongo.db.area.find({})
        area_list = []
        for a in areas:
            a.pop('_id')
            a.pop("parent_code")
            area_list.append(a)

        resp_data = {
            "province_list": province_list,
            "city_list": city_list,
            "area_list": area_list
        }

        return ResponseMaker.success(resp_data)
