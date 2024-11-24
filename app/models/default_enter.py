# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2024/9/11
Last Modified: 2024/9/11
Description: 
"""
from bson import ObjectId

from .basic import BasicModel


class DefaultEnterModel(BasicModel):
    """预设录入模型"""
    def __init__(self, req=None, db=None):
        if db is not None:
            super(DefaultEnterModel, self).__init__(db=db)
        else:
            super(DefaultEnterModel, self).__init__(req=req)

        self.collection_name = "default_enter"

    def is_exist(self, default_enter_id):
        """根据id，判断预设录入是否存在"""
        return super(DefaultEnterModel, self).is_exist(self.collection_name, default_enter_id)

    def get(self, enter_id):
        """根据预设录入id，获取预设录入数据"""
        condition = {"_id": ObjectId(enter_id)}
        default_enter = self.db[self.collection_name].find_one(condition)
        return default_enter

    def get_all(self):
        """获取全部预设录入数据"""
        default_enters = self.db[self.collection_name].find({})
        return default_enters

    def create(self, data):
        """创建预设录入"""
        name = data.get("name")

        default_enter_data = {
            "name": name
        }

        default_enter_data.update(self.get_create_meta())

        result = self.db[self.collection_name].insert_one(default_enter_data)
        return str(result.inserted_id)

    def update(self, enter_id, data):
        """修改预设录入"""
        condition = {"_id": ObjectId(enter_id)}

        default_enter_data = {
            "$set": {
                "name": data.get("name")
            }
        }

        default_enter_data["$set"].update(self.get_update_meta())

        self.db[self.collection_name].update_one(condition, default_enter_data)
        return enter_id

    def delete(self, enter_id):
        """删除预设录入"""
        condition = {"_id": ObjectId(enter_id)}

        self.db[self.collection_name].delete_one(condition)

    def query_list(self, page_number, page_size, keyword):
        """删除预设录入"""
        condition = {}

        if keyword:
            condition.update({"name": {"$regex": keyword}})

        start = (page_number - 1) * page_size
        default_enters = self.db[self.collection_name].find(condition).skip(start).limit(page_size)
        total = self.db[self.collection_name].count_documents(condition)

        list_data = {
            "total": total,
            "list": list(default_enters)
        }
        return list_data