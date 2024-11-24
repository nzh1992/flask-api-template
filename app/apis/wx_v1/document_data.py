# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2024/9/22
Last Modified: 2024/9/22
Description: 
"""
from flask import request, current_app
from flask_restx import Resource, Namespace, fields

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from app.models.document import Document
from app.models.document_data import DocumentDataModel
from utils.log import RequestLogUtil


wx_document_data_api = Namespace("app", description="移动端API", path="/app_api/v1/document")

wx_document_data_param_model = wx_document_data_api.model("DocumentDataParamModel", {
    "document_id": fields.String(required=True, description="档案id"),
    '种子名称': fields.String(required=False, description='自定义字段，取决于档案配置中的字段配置')
})

wx_document_data_list_model = wx_document_data_api.model("WXDocumentListModel", {
    'page_number': fields.Integer(required=True, description='页码', default=1),
    'page_size': fields.Integer(required=True, description='每页数量', default=10),
    'start_date': fields.String(required=True, description='培育周期-开始时间'),
    'end_date': fields.String(required=True, description='培育周期-结束时间'),
    'land_id': fields.String(required=False, description='关联土地id'),
    'keyword': fields.String(required=False, description='土地名称')
})

wx_document_data_list_model = wx_document_data_api.model('DocumentDataListModel', {
    'page_number': fields.Integer(required=True, description='页码', default=1),
    'page_size': fields.Integer(required=True, description='每页数量', default=10),
    'dataIndex': fields.String(required=False, description='列名，用哪一列匹配'),
    'keyword': fields.String(required=False, description='关键字，匹配的值')
})


@wx_document_data_api.route('/<document_id>/document_data/')
class DocumentDataAPI(Resource):
    @wx_document_data_api.doc(description='添加数据', body=wx_document_data_param_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def put(self, *args, **kwargs):
        document_id = request.view_args.get("document_id")

        data = request.get_json(force=True)

        doc_model = DocumentDataModel(req=request)
        result = doc_model.create(document_id, data)
        if not result.get("result"):
            return ResponseMaker.document_data_column_error(result.get("desc"))

        return ResponseMaker.success()


@wx_document_data_api.route('/<document_id>/document_data/<document_data_id>')
class DocumentDataAPI(Resource):
    @wx_document_data_api.doc(description='获取数据', params={"document_id": "档案id", "document_data_id": "数据id"})
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def get(self, *args, **kwargs):
        document_id = request.view_args.get("document_id")
        data_id = request.view_args.get("document_data_id")

        doc_model = DocumentDataModel(req=request)
        document_data = doc_model.get(document_id, data_id)
        if not document_data:
            return ResponseMaker.not_exist("档案数据", {})

        document_data.pop("_id")
        document_data["id"] = data_id

        return ResponseMaker.success(document_data)

    @wx_document_data_api.doc(description='修改数据', params={"document_id": "档案id", "document_data_id": "数据id"}, body=wx_document_data_param_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def post(self, *args, **kwargs):
        document_id = request.view_args.get("document_id")
        data_id = request.view_args.get("document_data_id")

        data = request.get_json(force=True)

        doc_model = DocumentDataModel(req=request)
        document_data = doc_model.get(document_id, data_id)
        if not document_data:
            return ResponseMaker.not_exist("档案数据", {})

        result = doc_model.update(document_id, data_id, data)
        if not result.get("result"):
            return ResponseMaker.document_data_column_error(result.get("desc"))

        return ResponseMaker.success()


@wx_document_data_api.route('/<document_id>/document_data/list')
class DocumentDataListAPI(Resource):
    @wx_document_data_api.doc(description='档案数据列表', body=wx_document_data_list_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def post(self, *args, **kwargs):
        document_id = request.view_args.get("document_id")

        data = request.get_json(force=True)
        page_number = data.get("page_number")
        page_size = data.get("page_size")
        data_index = data.get("dataIndex")
        keyword = data.get("keyword")  # 当前关键字为土地名称

        doc_model = DocumentDataModel(req=request)
        result = doc_model.query_list(document_id, page_number, page_size, data_index, keyword)

        document_data_list = []

        for d in result.get("list"):
            data_id = d.pop("_id")
            d["id"] = str(data_id)
            document_data_list.append(d)

        # 添加档案名称
        document_name = Document(req=request).get(document_id).get("document_name")

        resp = {
            "document_name": document_name,
            "total": result.get("total"),
            "list": document_data_list
        }

        return ResponseMaker.success(resp)