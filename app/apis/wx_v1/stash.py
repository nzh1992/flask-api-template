# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/13
Last Modified: 2023/12/13
Description: 
"""
from flask import request
from flask_restx import Resource, Namespace, fields

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from app.models.region import REGION
from app.models.stash import Stash
from utils.log import RequestLogUtil


wx_stash_api = Namespace("app", description="移动端API", path="/app_api/v1/stash")

wx_stash_list_model = wx_stash_api.model('WXStashListModel', {
    'pn': fields.String(required=True, description='页码'),
    'pz': fields.String(required=True, description='每页数量'),
    'status': fields.String(required=False, description='仓库状态'),
    'region': fields.List(fields.String, required=False, description='省市区'),
    'keyword': fields.String(required=False, description='仓库名称')
})

wx_stash_seed_list_model = wx_stash_api.model('WXStashSeedListModel', {
    'pn': fields.String(required=True, description='页码'),
    'pz': fields.String(required=True, description='每页数量'),
    'stash_id': fields.String(required=False, description='仓库id'),
    'keyword': fields.String(required=False, description='关键字（种子名称/种子编号）')
})


@wx_stash_api.route('/list')
class WXStashListAPI(Resource):
    @wx_stash_api.doc(description='仓库列表', body=wx_stash_list_model)
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
                "status": stash.get("status")
            }
            stash_data_list.append(stash_data)

        resp_data = {
            "total": result.get("total"),
            "list": stash_data_list
        }

        return ResponseMaker.success(resp_data)


@wx_stash_api.route('/inventory_list')
class WXStashInventoryListAPI(Resource):
    @wx_stash_api.doc(description='获取仓库种子列表', body=wx_stash_seed_list_model)
    @JWTUtil.verify_token_decorator(request)
    def post(self, *args, **kwargs):
        data = request.get_json(force=True)
        pn = data.get("pn")
        pz = data.get("pz")
        stash_id = data.get("stash_id")
        keyword = data.get("keyword")

        result = Stash(req=request).seed_list(pn, pz, stash_id, keyword)

        return ResponseMaker.success(result)
