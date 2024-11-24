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
from app.models.tencent_cos import TencentCos
from utils.log import RequestLogUtil


wx_upload_api = Namespace("app", description="客户端API", path="/app_api/v1/upload")


@wx_upload_api.route('/image')
class FileUploadAPI(Resource):
    @wx_upload_api.doc(description='上传图片')
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def post(self, *args, **kwargs):
        file = request.files['file']

        enterprise_id = request.user.get("enterprise_id")
        file_name = f"{enterprise_id}/land/{file.filename}"
        cos = TencentCos()
        url = cos.upload_image(file, file_name)

        resp_data = {
            "url": url
        }

        return ResponseMaker.success(resp_data)
