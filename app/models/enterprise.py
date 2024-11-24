# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/8
Last Modified: 2023/12/8
Description: 
"""
from bson import ObjectId

from .basic import BasicModel


class Enterprise(BasicModel):
    """
    企业信息
    """
    def __init__(self, req=None, db=None):
        if db is not None:
            super(Enterprise, self).__init__(db=db, req=req)
        else:
            super(Enterprise, self).__init__(req=req)

        self.collection_name = "enterprise"

    def is_exist(self, enterprise_id):
        """根据土地id，判断土地是否存在"""
        return super(Enterprise, self).is_exist(self.collection_name, enterprise_id)

    def init_data(self, data):
        """
        在程序运行时初始化数据。在管理后台创建企业接口中调用

        :param data: dict. 创建企业数据
        """
        count = self.db[self.collection_name].count_documents({})
        if count == 0:
            self.db[self.collection_name].insert_one(data)

    def get(self, enterprise_id):
        condition = {"_id": ObjectId(enterprise_id)}
        enterprise = self.db[self.collection_name].find_one(condition)
        return enterprise

    def update(self, enterprise_id, data):
        logo = data.get("logo")
        hotline = data.get("hotline")
        email = data.get("email")

        update_data = {
            "$set": {
                "logo": logo,
                "hotline": hotline,
                "email": email
            }
        }
        update_data['$set'].update(self.get_update_meta())
        self.db[self.collection_name].update_one({"_id": ObjectId(enterprise_id)}, update_data)