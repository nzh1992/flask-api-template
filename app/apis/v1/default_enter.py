# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2024/9/11
Last Modified: 2024/9/11
Description: 
"""
from flask import request
from flask_restx import Resource, Namespace, fields

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from app.models.default_enter import DefaultEnterModel
from utils.log import RequestLogUtil


default_enter_api = Namespace("client", description="客户端API", path="/client_api/v1/default_enter")


default_enter_model = default_enter_api.model('DefaultEnterModel', {
    'name': fields.String(required=True, description='预设录入内容')
})


default_enter_list_model = default_enter_api.model('DefaultEnterListModel', {
    'page_number': fields.Integer(required=True, description='页码', default=1),
    'page_size': fields.Integer(required=True, description='每页数量', default=10),
    'keyword': fields.String(required=False, description='关键字：预设录入内容')
})


@default_enter_api.route('/')
class DefaultEnterAPI(Resource):
    @default_enter_api.doc(description='创建预设录入', body=default_enter_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def put(self, *args, **kwargs):
        data = request.get_json(force=True)
        default_enter_model = DefaultEnterModel(req=request)
        default_enter_model.create(data)

        return ResponseMaker.success()


@default_enter_api.route('/<id>')
class DefaultEnterDetailAPI(Resource):
    @default_enter_api.doc(description='预设录入详情', params={'id': '预设录入id'})
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def get(self, *args, **kwargs):
        default_enter_id = request.view_args.get("id")
        default_enter_model = DefaultEnterModel(req=request)
        default_enter = default_enter_model.get(default_enter_id)
        if not default_enter:
            return ResponseMaker.not_exist("预设录入", {})

        default_enter_data = {
            "id": str(default_enter.get("_id")),
            "name": default_enter.get("name"),
        }

        return ResponseMaker.success(default_enter_data)

    @default_enter_api.doc(description='修改录入内容', params={'id': '预设录入id'}, body=default_enter_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def patch(self, *args, **kwargs):
        default_enter_id = request.view_args.get("id")
        data = request.get_json(force=True)

        default_enter_model = DefaultEnterModel(req=request)

        if not default_enter_model.is_exist( default_enter_id):
            return ResponseMaker.not_exist("预设录入", {})

        default_enter_model.update(default_enter_id, data)

        return ResponseMaker.success()

    @default_enter_api.doc(description='删除预设录入', params={'id': '预设录入id'})
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def delete(self, *args, **kwargs):
        default_enter_id = request.view_args.get("id")

        default_enter_model = DefaultEnterModel(req=request)

        if not default_enter_model.is_exist( default_enter_id):
            return ResponseMaker.not_exist("预设录入", {})

        default_enter_model.delete(default_enter_id)

        return ResponseMaker.success()


@default_enter_api.route('/list')
class DefaultEnterListAPI(Resource):
    @default_enter_api.doc(description='预设录入列表', body=default_enter_list_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def post(self, *args, **kwargs):
        data = request.get_json(force=True)
        page_number = data.get("page_number")
        page_size = data.get("page_size")
        keyword = data.get("keyword")

        default_enter_model = DefaultEnterModel(req=request)
        result = default_enter_model.query_list(page_number, page_size, keyword)

        default_enter_list = []

        for default_enter in result.get("list"):
            default_enter_data = {
                "id": str(default_enter.get("_id")),
                "name": default_enter.get("name"),
            }
            default_enter_list.append(default_enter_data)

        result["list"] = default_enter_list

        return ResponseMaker.success(result)


@default_enter_api.route('/all')
class DefaultEnterListAPI(Resource):
    @default_enter_api.doc(description='全部预设录入')
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def get(self, *args, **kwargs):
        default_enter_model = DefaultEnterModel(req=request)
        default_enters = default_enter_model.get_all()

        default_enter_list = []

        for default_enter in default_enters:
            default_enter_data = {
                "id": str(default_enter.get("_id")),
                "name": default_enter.get("name"),
            }
            default_enter_list.append(default_enter_data)

        return ResponseMaker.success(default_enter_list)