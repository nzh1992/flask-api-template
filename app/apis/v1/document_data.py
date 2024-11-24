# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2024/9/16
Last Modified: 2024/9/16
Description: 
"""
from io import BytesIO

import requests
from flask import request, send_file
from flask_restx import Resource, Namespace, fields
import pandas as pd

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from app.models.document import Document
from app.models.document_data import DocumentDataModel
from utils.log import RequestLogUtil


document_data_api = Namespace("client", description="客户端API", path="/client_api/v1/document")


document_data_param_model = document_data_api.model("DocumentDataParamModel", {
    "document_id": fields.String(required=True, description="档案id"),
    '种子名称': fields.String(required=False, description='自定义字段，取决于档案配置中的字段配置')
})

document_data_list_model = document_data_api.model('DocumentDataListModel', {
    'page_number': fields.Integer(required=True, description='页码', default=1),
    'page_size': fields.Integer(required=True, description='每页数量', default=10),
    'dataIndex': fields.String(required=False, description='列名，用哪一列匹配'),
    'keyword': fields.String(required=False, description='关键字，匹配的值')
})

document_data_import_model = document_data_api.model('DocumentDataImportModel', {
    'excel_url': fields.String(required=True, description='excel文件URL'),
    'import_type': fields.String(required=True, description='导入类型。枚举值：APPEND, COVER', default="APPEND"),
})


@document_data_api.route('/<document_id>/document_data/')
class DocumentDataAPI(Resource):
    @document_data_api.doc(description='添加数据', body=document_data_param_model)
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


@document_data_api.route('/<document_id>/document_data/<document_data_id>')
class DocumentDataAPI(Resource):
    @document_data_api.doc(description='获取数据', params={"document_id": "档案id", "document_data_id": "数据id"})
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

    @document_data_api.doc(description='修改数据', params={"document_id": "档案id", "document_data_id": "数据id"}, body=document_data_param_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def patch(self, *args, **kwargs):
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

    @document_data_api.doc(description='删除数据', params={"document_id": "档案id", "document_data_id": "数据id"})
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def delete(self, *args, **kwargs):
        document_id = request.view_args.get("document_id")
        data_id = request.view_args.get("document_data_id")

        doc_model = DocumentDataModel(req=request)
        document_data = doc_model.get(document_id, data_id)
        if not document_data:
            return ResponseMaker.not_exist("档案数据", {})

        doc_model.delete(document_id, data_id)

        return ResponseMaker.success()


@document_data_api.route('/<document_id>/document_data/list')
class DocumentDataListAPI(Resource):
    @document_data_api.doc(description='数据列表', body=document_data_list_model)
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


@document_data_api.route('/template/<id>')
class DocuemntTemplateAPI(Resource):
    @document_data_api.doc(description='下载模板', params={"id": "档案id"})
    @JWTUtil.verify_token_decorator(request)
    def get(self, *args, **kwargs):
        document_id = request.view_args.get("id")

        document_model = Document(req=request)
        document = document_model.get(document_id)
        if not document:
            return ResponseMaker.not_exist("档案", {})

        column_config_list = document.get("column_config_list")

        # 生成列名
        column_names = [c.get("dataIndex") for c in column_config_list]

        # 根据档案名称，生成excel模板文件名
        excel_name = f"{document.get('document_name')}模板.xlsx"

        # 将二进制数据写入内存对象
        bytes_io = BytesIO()

        # 生成excel
        df = pd.DataFrame(columns=column_names)
        df.to_excel(bytes_io, index=False)
        bytes_io.seek(0)

        return send_file(bytes_io, download_name=excel_name, as_attachment=True)


@document_data_api.route('/export/<id>')
class DocuemntExportAPI(Resource):
    @document_data_api.doc(description='导出全部数据', params={"id": "档案id"})
    @JWTUtil.verify_token_decorator(request)
    def get(self, *args, **kwargs):
        document_id = request.view_args.get("id")

        document_model = Document(req=request)
        document = document_model.get(document_id)
        if not document:
            return ResponseMaker.not_exist("档案", {})

        document_data_model = DocumentDataModel(req=request)
        datas = document_data_model.get_all(document_id)
        data_list = list(datas)

        # 根据档案名称，生成excel模板文件名
        excel_name = f"{document.get('document_name')}.xlsx"

        # 将二进制数据写入内存对象
        bytes_io = BytesIO()

        # 生成excel
        df = pd.DataFrame(data_list)
        df.to_excel(bytes_io, index=False)
        bytes_io.seek(0)

        return send_file(bytes_io, download_name=excel_name, as_attachment=True)


@document_data_api.route('/import/<id>')
class DocuemntExportAPI(Resource):
    @document_data_api.doc(description='通过excel导入数据', params={"id": "档案id"}, body=document_data_import_model)
    @JWTUtil.verify_token_decorator(request)
    def post(self, *args, **kwargs):
        document_id = request.view_args.get("id")

        data = request.get_json(force=True)
        excel_url = data.get("excel_url")
        import_type = data.get("import_type")

        document_model = Document(req=request)
        document = document_model.get(document_id)
        if not document:
            return ResponseMaker.not_exist("档案", {})

        try:
            # 读取档案配置
            column_config_list = document.get("column_config_list")
            column_names = [c.get("dataIndex") for c in column_config_list]

            # 从cos读取excel文件
            resp = requests.get(excel_url)
            content = resp.content
            df = pd.read_excel(content)

            # 生成数据
            insert_data_list = []
            for index, row in df.iterrows():
                insert_data = {}
                for column in column_names:
                    # 判断列名是否存在
                    if column not in column_names:
                        msg = f"档案中并未配置‘{column}’列"
                        return ResponseMaker.document_data_import_failed(msg)
                    else:
                        # 如果excel中该字段为空，置为空字符串
                        if pd.isna(row[column]):
                            value = ""
                        else:
                            value = row[column]

                        insert_data[column] = value

                insert_data_list.append(insert_data)

            document_data_model = DocumentDataModel(req=request)

            if import_type == "APPEND":
                # 追加导入
                document_data_model.import_append(document_id, insert_data_list)
            elif import_type == "COVER":
                # 覆盖导入
                document_data_model.import_cover(document_id, insert_data_list)
            else:
                return ResponseMaker.document_import_type_error()

            return ResponseMaker.success()
        except Exception as e:
            msg = str(e)
            return ResponseMaker.document_data_import_failed(msg)
