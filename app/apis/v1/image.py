# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/28
Last Modified: 2023/11/28
Description: 
"""
from flask import request, make_response, current_app
from flask_restx import Resource, Namespace
from utils.mongo import Mongo

from utils.response import ResponseMaker
from app.models.image import Image


image_api = Namespace("client", description="客户端API", path="/api/v1/image")

content_type_mapping = {
    ".png": "image/png",
    ".jpg": "image/jpg",
    ".jpeg": "image/jpeg"
}


@image_api.route('/')
class ImageAPI(Resource):
    @image_api.doc(description='图片在线加载', params={'image_id': '图片id'})
    def get(self, *args, **kwargs):
        image_id = request.args.get("image_id")
        short_name = request.args.get("short_name")

        if not Image.is_id_format_right(image_id):
            return ResponseMaker.id_format_error()

        # 缺少short_name，无法定位企业数据
        if not short_name:
            return ResponseMaker.short_name_missing()

        # 构造mongo连接
        host = current_app.config["MONGO_HOST"]
        port = current_app.config["MONGO_PORT"]
        db = Mongo(host, port).get_db(short_name)

        image_m = Image(db=db)
        if not image_m.is_exist(image_id):
            return ResponseMaker.image_not_exist()

        image = image_m.get(image_id)
        response = make_response(image.get("data"))

        # 根据图片类型设置header
        image_type = image.get("type")
        content_type = content_type_mapping.get(image_type)
        response.headers.set('Content-Type', content_type)

        return response
