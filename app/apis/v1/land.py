# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/22
Last Modified: 2023/11/22
Description: 土地管理
"""
from flask import request
from flask_restx import Resource, Namespace, fields

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from app.models.land import Land
from app.models.region import REGION
from utils.log import RequestLogUtil


land_api = Namespace("client", description="客户端API", path="/client_api/v1/land")

province_model = land_api.model('LandProvinceModel', {
    'name': fields.String(description="省"),
    'code': fields.String(description="省编码"),
})

city_model = land_api.model('LandCityModel', {
    'name': fields.String(description="市"),
    'code': fields.String(description="市编码"),
})

area_model = land_api.model('LandAreaModel', {
    'name': fields.String(description="区县"),
    'code': fields.String(description="区县编码"),
})

land_model = land_api.model('LandModel', {
    'land_name': fields.String(required=True, description='土地名称'),
    'province': fields.Nested(province_model, required=True, description='省'),
    'city': fields.Nested(city_model, required=True, description='市'),
    'area': fields.Nested(area_model, required=True, description='区县'),
    'detail_address': fields.String(required=True, description='详细地址'),
    'land_image_url': fields.String(required=False, description='土地图片URL')
})

land_list_model = land_api.model('LandListModel', {
    'page_number': fields.Integer(required=True, description='页码', default=1),
    'page_size': fields.Integer(required=True, description='每页数量', default=10),
    'province_code': fields.Nested(province_model, required=False, description='省编码'),
    'city_code': fields.Nested(city_model, required=False, description='市编码'),
    'area_code': fields.Nested(area_model, required=False, description='区县编码'),
    'status': fields.String(required=False, description='土地状态'),
    'keyword': fields.String(required=False, description='土地名称')
})

land_status_model = land_api.model('LandStatusModel', {
    'id': fields.String(required=True, description='土地id'),
    'status': fields.String(required=True, description='土地状态枚举值'),
})


@land_api.route('/')
class LandAPI(Resource):
    @land_api.doc(description='创建土地', body=land_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def put(self, *args, **kwargs):
        data = request.get_json(force=True)
        land = Land(req=request)
        result = land.create(data)
        if not result:
            return ResponseMaker.land_name_duplicated()

        return ResponseMaker.success()


@land_api.route('/<id>')
class LandDetailAPI(Resource):
    @land_api.doc(description='土地详情', params={'id': '土地id'})
    @JWTUtil.verify_token_decorator(request)
    def get(self, params, *args, **kwargs):
        land_id = request.view_args.get("id")
        if not Land.is_id_format_right(land_id):
            return ResponseMaker.id_format_error()

        land_m = Land(req=request)
        land = land_m.get(land_id)
        if not land:
            return ResponseMaker.not_exist("土地", {})

        land_data = {
            "id": str(land.get("_id")),
            "land_name": land.get("land_name"),
            "province": {
                "name": land.get("province_name"),
                "code": land.get("province_code"),
            },
            "city": {
                "name": land.get("city_name"),
                "code": land.get("city_code"),
            },
            "area": {
                "name": land.get("area_name"),
                "code": land.get("area_code"),
            },
            "detail_address": land.get("detail_address"),
            "status": land.get("status"),
            "land_image_url": land.get("land_image_url"),
        }

        return ResponseMaker.success(land_data)

    @land_api.doc(description='修改土地信息', params={'id': '土地id'}, body=land_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def patch(self, params, *args, **kwargs):
        land_id = request.view_args.get("id")
        if not Land.is_id_format_right(land_id):
            return ResponseMaker.id_format_error()

        land_m = Land(req=request)
        land = land_m.get(land_id)
        if not land:
            return ResponseMaker.not_exist("土地", {})

        data = request.get_json(force=True)
        result = land_m.update(land_id, data)

        if not result:
            return ResponseMaker.land_name_duplicated()

        return ResponseMaker.success()

    @land_api.doc(description='删除土地', params={'id': '土地id'})
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def delete(self, params, *args, **kwargs):
        land_id = request.view_args.get("id")
        if not Land.is_id_format_right(land_id):
            return ResponseMaker.id_format_error()

        land_m = Land(req=request)
        land = land_m.get(land_id)
        if not land:
            return ResponseMaker.not_exist("土地", {})

        # 检查土地是否使用中
        if land.get("status") == "USED":
            return ResponseMaker.land_is_used()

        land_m.delete(land_id)
        return ResponseMaker.success()


@land_api.route('/list')
class LandListAPI(Resource):
    @land_api.doc(description='土地列表', body=land_list_model)
    @JWTUtil.verify_token_decorator(request)
    def post(self, *args, **kwargs):
        data = request.get_json(force=True)
        page_number = data.get("page_number")
        page_size = data.get("page_size")
        province_code = data.get("province_code")
        city_code = data.get("city_code")
        area_code = data.get("area_code")
        status = data.get("status")
        keyword = data.get("keyword")       # 当前关键字为土地名称

        result = Land(req=request).query_list(page_number, page_size, province_code, city_code, area_code, status, keyword)

        # 对返回结果格式化
        land_datas = []
        for land in result.get("list"):
            land_data = {
                "id": str(land.get("_id")),
                "land_name": land.get("land_name"),
                "province": {
                    "name": land.get("province_name"),
                    "code": land.get("province_code"),
                },
                "city": {
                    "name": land.get("city_name"),
                    "code": land.get("city_code"),
                },
                "area": {
                    "name": land.get("area_name"),
                    "code": land.get("area_code"),
                },
                "detail_address": land.get("detail_address"),
                "status": land.get("status"),
                "land_image_url": land.get("land_image_url"),
            }
            land_datas.append(land_data)

        resp_data = {
            'total': result.get("total"),
            'list': land_datas
        }

        return ResponseMaker.success(resp_data)


@land_api.route('/all')
class AllLandAPI(Resource):
    @land_api.doc(description='全部土地')
    @JWTUtil.verify_token_decorator(request)
    def get(self, *args, **kwargs):
        result = Land(req=request).get_all()

        return ResponseMaker.success(result)