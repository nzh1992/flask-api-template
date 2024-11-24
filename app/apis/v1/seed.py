# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/30
Last Modified: 2023/11/30
Description: 
"""
from flask import request
from flask_restx import Resource, Namespace, fields

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from app.models.seed import Seed
from utils.log import RequestLogUtil


seed_api = Namespace("client", description="客户端API", path="/api/v1/seed")

seed_model = seed_api.model("SeedModel", {
    '种子名称': fields.String(required=True, description='种子名称'),
    '种子编号': fields.String(required=True, description='种子编号'),
    '父本': fields.String(required=True, description='父本'),
    '母本': fields.String(required=True, description='母本'),
    '审定': fields.Boolean(required=True, description='审定'),
    '审定编号': fields.String(required=True, description='审定编号')
})

seed_list_model = seed_api.model('SeedListModel', {
    'pn': fields.String(required=True, description='页码'),
    'pz': fields.String(required=True, description='每页数量'),
    'source': fields.String(required=False, description='来源，枚举值，CREATE/DOCUMENT'),
    '审定': fields.String(required=False, description='审定'),
    "stash_id": fields.String(required=False, description="仓库id"),
    'keyword': fields.String(required=False, description='关键字，种子名称/种子编号')
})


@seed_api.route('/')
class SeedAPI(Resource):
    @seed_api.doc(description='创建种子', body=seed_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def put(self, *args, **kwargs):
        data = request.get_json(force=True)
        name = data.get("种子名称")
        code = data.get("种子编号")

        seed_m = Seed(req=request)

        if seed_m.name_count(name) > 0:
            return ResponseMaker.seed_name_exist()

        if seed_m.code_count(code) > 0:
            return ResponseMaker.seed_code_exist()

        seed_m.create(data)
        return ResponseMaker.success()


@seed_api.route('/<id>')
class SeedDetailAPI(Resource):
    @seed_api.doc(description='种子详情', params={'id': "种子id"})
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

    @seed_api.doc(description='修改种子', params={'id': "种子id"})
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def patch(self, params, *args, **kwargs):
        seed_id = request.view_args.get("id")
        if not Seed.is_id_format_right(seed_id):
            return ResponseMaker.id_format_error()

        seed_m = Seed(req=request)
        if not seed_m.is_exist(seed_id):
            return ResponseMaker.not_exist("种子", {})

        data = request.get_json(force=True)
        name = data.get("种子名称")
        code = data.get("种子编号")

        if seed_m.name_count(name) > 1:
            return ResponseMaker.seed_name_exist()

        if seed_m.code_count(code) > 1:
            return ResponseMaker.seed_code_exist()

        seed_m.update(seed_id, data)

        return ResponseMaker.success()

    @seed_api.doc(description='删除种子', params={'id': "种子id"})
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def delete(self, params, *args, **kwargs):
        seed_id = request.view_args.get("id")
        if not Seed.is_id_format_right(seed_id):
            return ResponseMaker.id_format_error()

        seed_m = Seed(req=request)
        if not seed_m.is_exist(seed_id):
            return ResponseMaker.not_exist("种子", {})

        ref_list = seed_m.has_ref(seed_id)
        if ref_list:
            return ResponseMaker.seed_has_reference(ref_list)

        seed_m.delete(seed_id)

        return ResponseMaker.success()


@seed_api.route('/all')
class SeedAllAPI(Resource):
    @seed_api.doc(description='所有种子')
    @JWTUtil.verify_token_decorator(request)
    def get(self, *args, **kwargs):
        seed_data_list = Seed(req=request).get_all()
        return ResponseMaker.success(seed_data_list)


@seed_api.route('/list')
class SeedListAPI(Resource):
    @seed_api.doc(description='种子列表', body=seed_list_model)
    @JWTUtil.verify_token_decorator(request)
    def post(self, *args, **kwargs):
        data = request.get_json(force=True)
        pn = data.get("pn")
        pz = data.get("pz")
        source = data.get("source")
        is_approve = data.get("审定")
        stash_id = data.get("stash_id")
        keyword = data.get("keyword")

        resp_data = Seed(req=request).query_list(pn, pz, source, is_approve, stash_id, keyword)

        return ResponseMaker.success(resp_data)
