# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/2
Last Modified: 2023/12/2
Description: 
"""
import os

from flask import request, send_from_directory, current_app
from flask_restx import Resource, Namespace

from utils.mongo import Mongo
from app.models.excel import Excel
from app.models.document import Document


download_api = Namespace("client", description="客户端API", path="/api/v1/download")


@download_api.route('/document')
class DownloadDocumentAPI(Resource):
    @download_api.doc(description='下载档案', params={'id': "档案id"})
    def get(self, *args, **kwargs):
        document_id = request.args.get("id")
        enterprise_id = request.args.get("enterprise_id")

        mongo_host = current_app.config["MONGO_HOST"]
        mongo_port = current_app.config["MONGO_PORT"]
        db_name = f"NZY_{enterprise_id}"
        db = Mongo(mongo_host, mongo_port).get_db(db_name)

        document_m = Document(db=db)
        excel_fp = document_m.export_excel(document_id)

        f_dir, f_name = os.path.split(excel_fp)

        return send_from_directory(f_dir, f_name, as_attachment=True)


@download_api.route('/document_template')
class DownloadDocumentTemplateAPI(Resource):
    @download_api.doc(description='下载模板')
    def get(self, *args, **kwargs):

        f_dir = os.path.join(os.getcwd(), "data")
        f_name = "模版.xlsx"

        return send_from_directory(f_dir, f_name, as_attachment=True)


@download_api.route('/excel')
class DownloadDocumentTemplateAPI(Resource):
    @download_api.doc(description='下载excel')
    def get(self, *args, **kwargs):
        excel_id = request.args.get("excel_id")
        enterprise_id = request.args.get("enterprise_id")

        mongo_host = current_app.config["MONGO_HOST"]
        mongo_port = current_app.config["MONGO_PORT"]
        db_name = f"NZY_{enterprise_id}"
        db = Mongo(mongo_host, mongo_port).get_db(db_name)
        excel = Excel(db=db).get(excel_id)
        excel_name = excel.get("name")

        f_dir = os.path.join(os.getcwd(), "data")
        fp = os.path.join(f_dir, excel_name)
        with open(fp, 'wb') as f:
            f.write(excel.get("data"))

        return send_from_directory(f_dir, excel_name, as_attachment=True)