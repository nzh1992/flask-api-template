# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/8
Last Modified: 2023/12/8
Description: 
"""
from bson import ObjectId
from flask import current_app

from .basic import BasicModel


class Video(BasicModel):
    def __init__(self, req=None, db=None):
        if db is not None:
            super(Video, self).__init__(db=db)
        else:
            super(Video, self).__init__(req=req)

        self.collection_name = "video"

    def is_exist(self, video_id):
        return super(Video, self).is_exist(self.collection_name, video_id)

    def get(self, video_id):
        condition = {"_id": ObjectId(video_id)}
        video = self.db[self.collection_name].find_one(condition)
        return video

    def upload(self, video_file):
        """
        上传视频

        :param video_file: file. 视频文件对象
        :return:
        """
        video_data = {
            "name": video_file.filename,
            "data": video_file.stream.read()
        }
        result = self.db[self.collection_name].insert_one(video_data)
        inserted_id = str(result.inserted_id)

        # 企业short_name
        short_name = self.db.name

        # 返回下载url
        api_domain = current_app.config['CLIENT_DOMAIN']
        download_url = f"{api_domain}/api/v1/video/?video_id={inserted_id}&short_name={short_name}"

        url_obj = {
            "url": download_url,
            "id": inserted_id,
            "name": video_file.filename
        }
        return url_obj
