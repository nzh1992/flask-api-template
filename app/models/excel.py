# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/13
Last Modified: 2023/12/13
Description: excel对象模型
"""
from bson import ObjectId
from flask import current_app

from .basic import BasicModel


class Excel(BasicModel):
    def __init__(self, req=None, db=None):
        if db is not None:
            super(Excel, self).__init__(db=db)
        else:
            super(Excel, self).__init__(req=req)

        self.collection_name = "document_excel"

    def is_exist(self, excel_id):
        return super(Excel, self).is_exist(self.collection_name, excel_id)

    def get(self, excel_id):
        condition = {"_id": ObjectId(excel_id)}
        excel = self.db[self.collection_name].find_one(condition)
        return excel

    def upload(self, excel_file):
        """
        上传excel文件

        :param excel_file: file. excel文件
        :return: str. excel_id
        """
        excel_data = {
            "name": excel_file.filename,
            "data": excel_file.stream.read()
        }
        result = self.db[self.collection_name].insert_one(excel_data)
        inserted_id = str(result.inserted_id)

        # 企业id
        enterprise_id = self.user.get("enterprise_id")

        # 返回下载url
        api_domain = current_app.config['CLIENT_DOMAIN']
        download_url = f"{api_domain}/api/v1/download/excel?excel_id={inserted_id}&enterprise_id={enterprise_id}"

        url_obj = {
            "url": download_url,
            "id": inserted_id,
            "name": excel_file.filename
        }
        return url_obj
