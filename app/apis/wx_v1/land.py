# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/22
Last Modified: 2023/11/22
Description: 土地管理
"""
import os
import json

from flask import request
from flask_restx import Resource, Namespace, fields

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from app.models.land import Land
from app.models.region import REGION


wx_land_api = Namespace("app", description="移动端API", path="/app_api/v1/land")

wx_land_list_model = wx_land_api.model('WXLandListModel', {
    'pn': fields.String(required=True, description='页码'),
    'pz': fields.String(required=True, description='每页数量'),
    'region': fields.List(fields.String, required=False, description='省市区'),
    'status': fields.String(required=False, description='土地状态'),
    'keyword': fields.String(required=False, description='土地名称')
})


@wx_land_api.route('/<id>')
class LandDetailAPI(Resource):
    @wx_land_api.doc(description='土地详情', params={'id': '土地id'})
    @JWTUtil.verify_token_decorator(request)
    def get(self, params, *args, **kwargs):
        land_id = request.view_args.get("id")
        if not Land.is_id_format_right(land_id):
            return ResponseMaker.id_format_error()

        land_m = Land(req=request)
        land = land_m.get(land_id)
        if not land:
            return ResponseMaker.not_exist("土地", {})

        code_list = [land.get("province_code"), land.get("city_code"), land.get("area_code")]
        province_name, city_name, area_name = REGION.code_to_name(code_list)

        land_data = {
            "name": land.get("name"),
            "region": f"{province_name}-{city_name}-{area_name}",
            "detail_address": land.get("detail_address"),
            "longitude": land.get("longitude"),
            "latitude": land.get("latitude"),
            "description": land.get("description")
        }

        return ResponseMaker.success(land_data)


@wx_land_api.route('/list')
class LandListAPI(Resource):
    @wx_land_api.doc(description='土地列表', body=wx_land_list_model)
    @JWTUtil.verify_token_decorator(request)
    def post(self, *args, **kwargs):
        data = request.get_json(force=True)
        pn = data.get("pn")
        pz = data.get("pz")
        region = data.get("region")
        status = data.get("status")
        keyword = data.get("keyword")  # 当前关键字为土地名称

        result = Land(req=request).query_list(pn, pz, region, status, keyword)

        # 对返回结果格式化
        land_datas = []
        for land in result.get("list"):
            # code -> name
            province_code = land.get("province_code")
            city_code = land.get("city_code")
            area_code = land.get("area_code")
            land_region = [province_code, city_code, area_code]
            province_name, city_name, area_name = REGION.code_to_name(land_region)

            land_data = {
                "id": str(land.get("_id")),
                "name": land.get("name"),
                "region": f"{province_name}-{city_name}-{area_name}",
                "status": land.get("status")
            }
            land_datas.append(land_data)

        resp_data = {
            'total': result.get("total"),
            'list': land_datas
        }

        return ResponseMaker.success(resp_data)
