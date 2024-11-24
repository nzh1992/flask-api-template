# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/8
Last Modified: 2023/12/8
Description: 
"""
import os

from bson import ObjectId
from flask import current_app

from .basic import BasicModel


class Image(BasicModel):
    def __init__(self, req=None, db=None):
        if db is not None:
            super(Image, self).__init__(db=db)
        else:
            super(Image, self).__init__(req=req)

        self.collection_name = "image"

    def is_exist(self, image_id):
        return super(Image, self).is_exist(self.collection_name, image_id)

    def get(self, image_id):
        condition = {"_id": ObjectId(image_id)}
        image = self.db[self.collection_name].find_one(condition)
        return image

    def upload(self, image_file):
        """
        上传图片

        :param image_file: file. 图片文件对象
        :return:
        """
        # 图片文件后缀名，作为图片类型
        image_type = os.path.splitext(image_file.filename)[-1]

        image_data = {
            "name": image_file.filename,
            "type": image_type,
            "data": image_file.stream.read()
        }
        result = self.db[self.collection_name].insert_one(image_data)
        inserted_id = str(result.inserted_id)

        # 企业short_name
        short_name = self.db.name

        # 返回下载url
        api_domain = current_app.config['CLIENT_DOMAIN']
        download_url = f"{api_domain}/api/v1/image/?image_id={inserted_id}&short_name={short_name}"

        url_obj = {
            "url": download_url,
            "id": inserted_id,
            "name": image_file.filename
        }
        return url_obj
