# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/8
Last Modified: 2023/12/8
Description: 封装pymongo
"""
from pymongo import MongoClient


class Mongo:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        try:
            self.client = MongoClient(host=host, port=port)
        except Exception as e:
            raise e

    def get_db_by_name(self, db_name):
        """根据名称获取数据库连接"""
        return self.client[db_name]

    def get_db_by_request(self, request):
        """根据请求中的user.enterprise_id获取对应数据库连接"""
        enterprise_id = request.user.get("enterprise_id")
        if not enterprise_id:
            raise Exception("从request中获取enterprise_id失败")

        db_name = f"NZY_{enterprise_id}"
        return self.get_db_by_name(db_name)


    def get_collection(self, db_name, collection_name):
        """获取集合"""
        return self.client[db_name][collection_name]
