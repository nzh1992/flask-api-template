# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/5
Last Modified: 2023/12/5
Description: 
"""
import os

from flask import request, current_app, send_file
from flask_restx import Resource, Namespace

from utils.response import ResponseMaker
from app.models.video import Video
from utils.mongo import Mongo


video_api = Namespace("client", description="客户端API", path="/api/v1/video")


@video_api.route('/')
class VideoAPI(Resource):
    @video_api.doc(description='视频在线播放', params={'video_id': '视频id'})
    def get(self, *args, **kwargs):
        video_id = request.args.get("video_id")
        short_name = request.args.get("short_name")

        if not Video.is_id_format_right(video_id):
            return ResponseMaker.id_format_error()

        # 缺少short_name，无法定位企业数据
        if not short_name:
            return ResponseMaker.short_name_missing()

        # 构造mongo连接
        host = current_app.config["MONGO_HOST"]
        port = current_app.config["MONGO_PORT"]
        db = Mongo(host, port).get_db(short_name)

        video_m = Video(db=db)
        if not video_m.is_exist(video_id):
            return ResponseMaker.not_exist("视频", {})

        video = video_m.get(video_id)
        video_file_name = video.get("name")
        tmp_fp = os.path.join(os.getcwd(), "data", video_file_name)
        with open(tmp_fp, "wb") as f:
            f.write(video.get("data"))

        return send_file(tmp_fp, mimetype="video/mp4")
