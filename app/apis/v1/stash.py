# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/30
Last Modified: 2023/11/30
Description: 仓库
"""
from flask import request
from flask_restx import Resource, Namespace, fields

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from app.models.region import REGION
from app.models.stash import Stash
from utils.log import RequestLogUtil


stash_api = Namespace("client", description="客户端API", path="/api/v1/stash")

stash_list_model = stash_api.model('StashListModel', {
    'pn': fields.String(required=True, description='页码'),
    'pz': fields.String(required=True, description='每页数量'),
    'status': fields.String(required=False, description='仓库状态'),
    'region': fields.List(fields.String, required=False, description='省市区'),
    'keyword': fields.String(required=False, description='仓库名称')
})

inventory_item_model = stash_api.model('InventoryList', {
    "name": fields.String(description="种子名称"),
    "code": fields.String(description="种子编号"),
    "id": fields.String(description="种子id"),
    "quantity": fields.String(description="种子数量"),
    "weight": fields.String(description="种子重量")
})

stash_model = stash_api.model('StashModel', {
    'name': fields.String(required=True, description='仓库名称'),
    'region': fields.List(fields.String, required=True, description='省市区'),
    'detail_address': fields.String(required=True, description='详细地址'),
    'description': fields.String(required=True, description='描述'),
    'inventory_list': fields.List(fields.Nested(inventory_item_model), required=True, description='描述'),
})

stash_status_model = stash_api.model('StashStatusModel', {
    'id': fields.String(required=True, description='仓库id'),
    'status': fields.String(required=True, description='仓库状态')
})


@stash_api.route('/')
class StashAPI(Resource):
    @stash_api.doc(description='创建仓库', body=stash_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def put(self, *args, **kwargs):
        data = request.get_json(force=True)
        Stash(req=request).create(data)
        return ResponseMaker.success()


@stash_api.route('/<id>')
class StashDetailAPI(Resource):
    @stash_api.doc(description='仓库详情', params={'id': "仓库id"})
    @JWTUtil.verify_token_decorator(request)
    def get(self, params, *args, **kwargs):
        stash_id = request.view_args.get("id")
        if not Stash.is_id_format_right(stash_id):
            return ResponseMaker.id_format_error()

        stash_m = Stash(req=request)
        if not stash_m.is_exist(stash_id):
            return ResponseMaker.not_exist("仓库", {})

        stash = stash_m.get(stash_id)

        stash_data = {
            "id": str(stash.get("_id")),
            "name": stash.get("name"),
            "region": [
                stash.get("province_code"),
                stash.get("city_code"),
                stash.get("area_code")
            ],
            "detail_address": stash.get("detail_address"),
            "description": stash.get("description"),
            "inventory_list": stash.get("inventory_list")
        }

        return ResponseMaker.success(stash_data)

    @stash_api.doc(description='修改仓库', params={'id': "仓库id"})
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def patch(self, params, *args, **kwargs):
        stash_id = request.view_args.get("id")
        if not Stash.is_id_format_right(stash_id):
            return ResponseMaker.id_format_error()

        stash_m = Stash(req=request)
        if not stash_m.is_exist(stash_id):
            return ResponseMaker.not_exist("仓库", {})

        data = request.get_json(force=True)
        stash_m.update(stash_id, data)
        return ResponseMaker.success()

    @stash_api.doc(description='删除仓库', params={'id': "仓库id"})
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def delete(self, params, *args, **kwargs):
        stash_id = request.view_args.get("id")
        if not Stash.is_id_format_right(stash_id):
            return ResponseMaker.id_format_error()

        stash_m = Stash(req=request)
        if not stash_m.is_exist(stash_id):
            return ResponseMaker.not_exist("仓库", {})

        # 已启用的仓库无法删除
        stash = stash_m.get(stash_id)
        if stash.get("status") == "ENABLE":
            return ResponseMaker.stash_is_enable()

        stash_m.delete(stash_id)
        return ResponseMaker.success()


@stash_api.route('/list')
class StashListAPI(Resource):
    @stash_api.doc(description='仓库列表', body=stash_list_model)
    @JWTUtil.verify_token_decorator(request)
    def post(self, *args, **kwargs):
        data = request.get_json(force=True)
        pn = data.get("pn")
        pz = data.get("pz")
        status = data.get("status")
        region = data.get("region")
        keyword = data.get("keyword")

        result = Stash(req=request).query_list(pn, pz, status, region, keyword)

        stash_data_list = []
        for stash in result.get("list"):
            province_code = stash.get("province_code")
            city_code = stash.get("city_code")
            area_code = stash.get("area_code")
            region_codes = [province_code, city_code, area_code]
            province_name, city_name, area_name = REGION.code_to_name(region_codes)
            stash_data = {
                "id": str(stash.get("_id")),
                "name": stash.get("name"),
                "region": f"{province_name}-{city_name}-{area_name}",
                "detail_address": stash.get("detail_address"),
                "description": stash.get("description"),
                "status": stash.get("status")
            }
            stash_data_list.append(stash_data)

        resp_data = {
            "total": result.get("total"),
            "list": stash_data_list
        }

        return ResponseMaker.success(resp_data)


@stash_api.route('/status')
class StashStatusAPI(Resource):
    @stash_api.doc(description='修改仓库状态', body=stash_status_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def post(self, *args, **kwargs):
        data = request.get_json(force=True)
        stash_id = data.get("id")
        status = data.get("status")

        if not Stash.is_id_format_right(stash_id):
            return ResponseMaker.id_format_error()

        stash_m = Stash(req=request)
        if not stash_m.is_exist(stash_id):
            return ResponseMaker.not_exist("仓库", {})

        stash_m.change_status(stash_id, status)

        return ResponseMaker.success()


@stash_api.route('/all')
class StashAllAPI(Resource):
    @stash_api.doc(description='全部仓库')
    @JWTUtil.verify_token_decorator(request)
    def get(self, *args, **kwargs):
        all_stash = Stash(req=request).get_all()
        return ResponseMaker.success(all_stash)
