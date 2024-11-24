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
from app.models.seed import Seed
from utils.log import RequestLogUtil


wx_seed_api = Namespace("app", description="移动端API", path="/app_api/v1/seed")

wx_seed_list_model = wx_seed_api.model('WXSeedListModel', {
    'pn': fields.String(required=True, description='页码'),
    'pz': fields.String(required=True, description='每页数量'),
    'source': fields.String(required=False, description='来源，枚举值，CREATE/DOCUMENT'),
    '审定': fields.String(required=False, description='审定'),
    "stash": fields.String(required=False, description="仓库id"),
    'keyword': fields.String(required=False, description='关键字，种子名称/种子编号')
})


@wx_seed_api.route('/list')
class WXSeedListAPI(Resource):
    @wx_seed_api.doc(description='种子列表', body=wx_seed_list_model)
    @JWTUtil.verify_token_decorator(request)
    def post(self, *args, **kwargs):
        data = request.get_json(force=True)
        pn = data.get("pn")
        pz = data.get("pz")
        source = data.get("source")
        keyword = data.get("keyword")

        resp_data = Seed(req=request).wx_query_list(pn, pz, source, keyword)

        return ResponseMaker.success(resp_data)


@wx_seed_api.route('/<id>')
class WXSeedDetailAPI(Resource):
    @wx_seed_api.doc(description='种子详情', params={'id': "种子id"})
    @JWTUtil.verify_token_decorator(request)
    def get(self, params, *args, **kwargs):
        seed_id = request.view_args.get("id")
        if not Seed.is_id_format_right(seed_id):
            return ResponseMaker.id_format_error()

        seed_m = Seed(req=request)
        if not seed_m.is_exist(seed_id):
            return ResponseMaker.not_exist("种子", {})

        seed = seed_m.get(seed_id)

        seed_data = {
            "id": str(seed.get("_id")),
            "种子名称": seed.get("种子名称"),
            "种子编号": seed.get("种子编号"),
            "父本": seed.get("父本"),
            "母本": seed.get("母本"),
            "审定": seed.get("审定"),
            "审定编号": seed.get("审定编号")
        }

        return ResponseMaker.success(seed_data)


@wx_seed_api.route('/all')
class WXSeedAllAPI(Resource):
    @wx_seed_api.doc(description='所有种子')
    @JWTUtil.verify_token_decorator(request)
    def get(self, *args, **kwargs):
        seed_data_list = Seed(req=request).get_all()
        return ResponseMaker.success(seed_data_list)