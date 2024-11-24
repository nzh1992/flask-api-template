# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/11
Last Modified: 2023/12/11
Description: 
"""
from bson import ObjectId

from .basic import BasicModel


class RequestLogModel(BasicModel):
    """
    请求日志模型
    """
    def __init__(self, req=None, db=None):
        if db is not None:
            super(RequestLogModel, self).__init__(db=db)
        else:
            super(RequestLogModel, self).__init__(req=req)

        self.collection_name = "sys_log_request"

    def create(self, log_data):
        """创建请求记录"""
        result = self.db[self.collection_name].insert_one(log_data)
        return str(result.inserted_id)

    def update(self, log_id, update_data):
        """更新请求记录"""
        condition = {"_id": ObjectId(log_id)}
        update_info = {
            "$set": update_data
        }
        self.db[self.collection_name].update_one(condition, update_info)
