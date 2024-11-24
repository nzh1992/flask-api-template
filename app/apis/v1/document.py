# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/27
Last Modified: 2023/11/27
Description: 档案API
"""
from urllib import parse

from flask import request, current_app
from flask_restx import Resource, Namespace, fields

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from app.models.document import Document
from app.models.land import Land
from utils.log import RequestLogUtil


document_api = Namespace("client", description="客户端API", path="/client_api/v1/document")

column_config_model = document_api.model("ColumnConfigModel", {
    "dataIndex": fields.String(required=True, description="字段名称"),
    "dataType": fields.String(required=True, description="数据类型")
})

document_model = document_api.model("DocumentModel", {
    'document_name': fields.String(required=True, description='档案名称'),
    'start_date': fields.String(required=True, description='培育周期-开始时间'),
    'end_date': fields.String(required=True, description='培育周期-结束时间'),
    'land_id': fields.String(required=True, description='关联土地id'),
    'column_config_list': fields.List(fields.Nested(column_config_model), required=True, description="列配置")
})

document_list_model = document_api.model('DocumentListModel', {
    'page_number': fields.Integer(required=True, description='页码', default=1),
    'page_size': fields.Integer(required=True, description='每页数量', default=10),
    'start_date': fields.String(required=True, description='培育周期-开始时间'),
    'end_date': fields.String(required=True, description='培育周期-结束时间'),
    'land_id': fields.String(required=False, description='关联土地id'),
    'keyword': fields.String(required=False, description='关键字：档案名称')
})


@document_api.route('/')
class DocumentAPI(Resource):
    @document_api.doc(description='创建档案', body=document_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def put(self, *args, **kwargs):
        data = request.get_json(force=True)

        # 检查列配置，列名不能重复
        column_config_list = data.get("column_config_list")
        data_index_list = [c.get("dataIndex") for c in column_config_list]
        data_index_unique_list = []
        data_index_duplicate_list = []
        for data_index in data_index_list:
            if data_index not in data_index_unique_list:
                data_index_unique_list.append(data_index)
            else:
                data_index_duplicate_list.append(data_index)

        # 如果有重复列，将重新列名返回给前端
        if len(data_index_unique_list) != len(data_index_list):
            duplicate_columns = ",".join(data_index_duplicate_list)
            return ResponseMaker.document_column_name_duplicated(duplicate_columns)

        document_model = Document(req=request)
        if document_model.is_exist_by_name(data.get("document_name")):
            return ResponseMaker.document_name_duplicated()

        document_model.create(data)

        return ResponseMaker.success()


@document_api.route('/<id>')
class DocumentDetailAPI(Resource):
    @document_api.doc(description='档案详情', params={'id': '档案id'})
    @JWTUtil.verify_token_decorator(request)
    def get(self, params, *args, **kwargs):
        document_id = request.view_args.get("id")
        if not Document.is_id_format_right(document_id):
            return ResponseMaker.id_format_error()

        document = Document(req=request).get(document_id)
        if not document:
            return ResponseMaker.not_exist("档案", {})

        # land = Land(req=request).get(document.get("land_id"))
        # if not land:
        #     return ResponseMaker.not_exist(f"档案相关土地id：{document.get('land_id')}")

        document_meta = {
            "id": str(document.get("_id")),
            "document_name": document.get("document_name"),
            "start_date": document.get("start_date"),
            "end_date": document.get("end_date"),
            "land_id": document.get("land_id"),
            "column_config_list": document.get("column_config_list"),
        }

        return ResponseMaker.success(document_meta)

    @document_api.doc(description='修改档案',  params={'id': '档案id'}, body=document_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def patch(self, params, *args, **kwargs):
        document_id = request.view_args.get("id")
        if not Document.is_id_format_right(document_id):
            return ResponseMaker.id_format_error()

        data = request.get_json(force=True)

        # 检查列配置，列名不能重复
        column_config_list = data.get("column_config_list")
        data_index_list = [c.get("dataIndex") for c in column_config_list]
        data_index_unique_list = []
        data_index_duplicate_list = []
        for data_index in data_index_list:
            if data_index not in data_index_unique_list:
                data_index_unique_list.append(data_index)
            else:
                data_index_duplicate_list.append(data_index)

        # 如果有重复列，将重新列名返回给前端
        if len(data_index_unique_list) != len(data_index_list):
            duplicate_columns = ",".join(data_index_duplicate_list)
            return ResponseMaker.document_column_name_duplicated(duplicate_columns)

        # 检查档案名称是否重复
        document_m = Document(req=request)
        if document_m.is_exist_on_update(data.get("document_name")):
            return ResponseMaker.document_name_duplicated()

        document_m.update(document_id, data)
        return ResponseMaker.success()

    @document_api.doc(description='删除档案')
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def delete(self, params, *args, **kwargs):
        document_id = request.view_args.get("id")
        if not Document.is_id_format_right(document_id):
            return ResponseMaker.id_format_error()

        document_m = Document(req=request)
        if not document_m.is_exist(document_id):
            return ResponseMaker.not_exist("档案", {})

        document_m.delete(document_id)

        return ResponseMaker.success()


@document_api.route('/list')
class DocumentListAPI(Resource):
    @document_api.doc(description='档案列表', body=document_list_model)
    @JWTUtil.verify_token_decorator(request)
    def post(self, *args, **kwargs):
        data = request.get_json(force=True)
        page_number = data.get("page_number")
        page_size = data.get("page_size")
        start_date = data.get("start_date")  # 培育周期
        end_date = data.get("end_date")      # 培育周期
        land_id = data.get("land_id")
        keyword = data.get("keyword")        # 当前关键字为土地名称

        query_result = Document(req=request).query_list(page_number, page_size, start_date, end_date, land_id, keyword)

        document_datas = []
        for document in query_result.get("list"):
            # 关联的土地
            land = Land(req=request).get(document.get("land_id"))

            document_data = {
                "id": str(document.get("_id")),
                "document_name": document.get("document_name"),
                "start_date": document.get("start_date"),
                "end_date": document.get("end_date"),
                "land_name": land.get("land_name")
            }
            document_datas.append(document_data)

        resp_data = {
            'total': query_result.get("total"),
            'list': document_datas
        }

        return ResponseMaker.success(resp_data)


@document_api.route('/config/<id>')
class DocumentConfigAPI(Resource):
    @document_api.doc(description='获取档案配置', params={'id': '档案id'})
    @JWTUtil.verify_token_decorator(request)
    def get(self, params, *args, **kwargs):
        document_id = request.view_args.get("id")
        if not Document.is_id_format_right(document_id):
            return ResponseMaker.id_format_error()

        document = Document(req=request).get(document_id)
        if not document:
            return ResponseMaker.not_exist("档案", {})

        column_config_list = document.get("column_config_list")

        return ResponseMaker.success(column_config_list)