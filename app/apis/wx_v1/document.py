# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/13
Last Modified: 2023/12/13
Description: 
"""
from flask import request, current_app
from flask_restx import Resource, Namespace, fields

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from app.models.document import Document
from app.models.land import Land
from utils.log import RequestLogUtil


wx_document_api = Namespace("app", description="移动端API", path="/app_api/v1/document")

wx_document_list_model = wx_document_api.model("WXDocumentListModel", {
    'page_number': fields.Integer(required=True, description='页码', default=1),
    'page_size': fields.Integer(required=True, description='每页数量', default=10),
    'start_date': fields.String(required=True, description='培育周期-开始时间'),
    'end_date': fields.String(required=True, description='培育周期-结束时间'),
    'land_id': fields.String(required=False, description='关联土地id'),
    'keyword': fields.String(required=False, description='土地名称')
})


@wx_document_api.route('/list')
class DocumentListAPI(Resource):
    @wx_document_api.doc(description='档案列表', body=wx_document_list_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def post(self, *args, **kwargs):
        data = request.get_json(force=True)
        page_number = data.get("page_number")
        page_size = data.get("page_size")
        start_date = data.get("start_date")  # 培育周期
        end_date = data.get("end_date")  # 培育周期
        land_id = data.get("land_id")
        keyword = data.get("keyword")  # 当前关键字为土地名称

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


@wx_document_api.route('/config/<id>')
class DocumentConfigAPI(Resource):
    @wx_document_api.doc(description='获取档案配置', params={'id': '档案id'})
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