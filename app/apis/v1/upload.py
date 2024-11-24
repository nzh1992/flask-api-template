# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/21
Last Modified: 2023/11/21
Description: 文件操作
"""
from flask import request
from flask_restx import Resource, Namespace

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
# from app.models.image import Image
from app.models.tencent_cos import TencentCos
from app.models.video import Video
from app.models.excel import Excel
from utils.log import RequestLogUtil


upload_api = Namespace("client", description="客户端API", path="/client_api/v1/upload")


@upload_api.route('/image')
class FileUploadAPI(Resource):
    @upload_api.doc(description='上传图片')
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def post(self, *args, **kwargs):
        file = request.files['file']
        # url_obj = Image(req=request).upload(file)

        enterprise_id = request.user.get("enterprise_id")
        file_name = f"{enterprise_id}/land/{file.filename}"
        cos = TencentCos()
        url = cos.upload_image(file, file_name)

        resp_data = {
            "url": url
        }

        return ResponseMaker.success(resp_data)


# @upload_api.route('/video')
# class FileUploadAPI(Resource):
#     @upload_api.doc(description='视频上传')
#     @JWTUtil.verify_token_decorator(request)
#     @RequestLogUtil.log(request)
#     def post(self, *args, **kwargs):
#         file = request.files['file']
#         url_obj = Video(req=request).upload(file)
#
#         return ResponseMaker.success(url_obj)


@upload_api.route('/excel')
class ExcelUploadAPI(Resource):
    @upload_api.doc(description='上传Excel')
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def post(self, *args, **kwargs):
        file = request.files['file']

        enterprise_id = request.user.get("enterprise_id")
        file_name = f"{enterprise_id}/excel/{file.filename}"
        cos = TencentCos()
        url = cos.upload_excel(file, file_name)

        resp_data = {
            "url": url
        }

        return ResponseMaker.success(resp_data)