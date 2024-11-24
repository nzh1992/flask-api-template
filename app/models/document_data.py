# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2024/9/16
Last Modified: 2024/9/16
Description: 
"""
import os
import json

from flask import current_app
from bson import ObjectId
import pandas as pd

from .basic import BasicModel
from .land import Land
from app.models.qr_code import QRCode
from utils.dt import DateTime


class DocumentDataModel(BasicModel):
    """
    档案数据模型类
    """
    def __init__(self, req=None, db=None):
        if db is not None:
            super(DocumentDataModel, self).__init__(db=db)
        else:
            super(DocumentDataModel, self).__init__(req=req)

        # 档案表表名
        self.document_name = "document"
        # 档案数据表表名，需要根据档案id动态计算
        self.data_name = None

    def create(self, doc_id, data):
        """
        创建档案数据

        :param doc_id: str. 档案id
        :param data: dict. 一条档案数据
        :return:
        """
        # 指定写入的表名
        self.data_name = f"data_{doc_id}"

        # 检查列名和档案配置是否匹配
        check_result = self._check_data_index(doc_id, data)
        if not check_result.get("result"):
            return check_result

        self.db[self.data_name].insert_one(data)
        resp = {"result": True}
        return resp

    def get(self, doc_id, data_id):
        """
        获取档案数据

        :param doc_id: str. 档案id
        :param data_id: str. 数据id
        :return:
        """
        # 指定写入的表名
        self.data_name = f"data_{doc_id}"

        data = self.db[self.data_name].find_one({"_id": ObjectId(data_id)})
        return data

    def update(self, doc_id, data_id, data):
        """
        修改数据

        :param doc_id: str. 档案id
        :param data_id: str. 数据id
        :param data: dict. 更新数据
        :return:
        """
        # 指定写入的表名
        self.data_name = f"data_{doc_id}"

        condition = {"_id": ObjectId(data_id)}
        update_data = {"$set": data}

        # 检查列名和档案配置是否匹配
        check_result = self._check_data_index(doc_id, data)
        if not check_result.get("result"):
            return check_result

        self.db[self.data_name].update_one(condition, update_data)
        resp = {"result": True}
        return resp

    def delete(self, doc_id, data_id):
        # 指定写入的表名
        self.data_name = f"data_{doc_id}"

        condition = {"_id": ObjectId(data_id)}
        self.db[self.data_name].delete_one(condition)

    def query_list(self, doc_id, page_number, page_size, data_index=None, keyword=None):
        """
        查询数据列表

        :param doc_id: str. 档案id
        :param page_number: int. 当前页数
        :param page_size: int. 每页数量
        :param data_index: str. 列名，根据哪一列进行匹配
        :param keyword: str. 关键字，用于匹配的值
        :return:
        """
        # 指定写入的表名
        self.data_name = f"data_{doc_id}"

        condition = {}

        if data_index and keyword:
            regex_condition = {
                data_index: {"$regex": keyword}
            }
            condition.update(regex_condition)

        start = (page_number - 1) * page_size

        document_datas = self.db[self.data_name].find(condition).skip(start).limit(page_size)
        total = self.db[self.data_name].count_documents(condition)

        document_data_list = list(document_datas)

        result = {
            "total": total,
            "list": document_data_list
        }
        return result

    def get_all(self, doc_id):
        """获取全部数据"""
        # 指定写入的表名
        self.data_name = f"data_{doc_id}"

        datas = self.db[self.data_name].find({}, {'_id': 0})
        return datas

    def import_append(self, doc_id, data_list):
        """
        多条数据批量导入(追加)

        :param doc_id: str. 档案id
        :param data_list: list. 档案数据列表
        :return:
        """
        # 指定写入的表名
        self.data_name = f"data_{doc_id}"

        datas = self.db[self.data_name].insert_many(data_list)
        return datas

    def import_cover(self, doc_id, data_list):
        """
        多条数据批量导入(覆盖)

        :param doc_id: str. 档案id
        :param data_list: list. 档案数据列表
        :return:
        """
        # 指定写入的表名
        self.data_name = f"data_{doc_id}"

        # 清空表
        self.db[self.data_name].delete_many({})

        datas = self.db[self.data_name].insert_many(data_list)
        return datas

    def _check_data_index(self, doc_id, data):
        """
        检查列名和档案配置是否匹配

        :param doc_id: str. 档案id
        :param data: dict. 一条档案数据
        :return:
        """
        column_config_list = self._get_column_config_list(doc_id)
        column_names = [c.get("dataIndex") for c in column_config_list]

        # 多余的列名
        more_column_list = []

        for k, v in data.items():
            if k not in column_names:
                more_column_list.append(k)

        # 缺少的列名
        less_set = set(column_names) - set(data.keys())
        less_column_list = list(less_set)

        # 默认返回值
        resp = {
            "result": True,
            "desc": "ok",
        }

        # 文字描述
        desc = "列名不匹配。"
        if more_column_list:
            desc += "多出的列名：" + "，".join(more_column_list) + "。"

        if less_column_list:
            desc += "缺少的列名：" + "，".join(less_column_list) + "。"

        if more_column_list or less_column_list:
            resp["result"] = False
            resp["desc"] = desc

        return resp


    def _get_column_config_list(self, doc_id):
        """
        获取档案的配置

        :param doc_id: str. 档案id
        :return:
        """
        condition = {"_id": ObjectId(doc_id)}
        document = self.db[self.document_name].find_one(condition)
        if not document:
            return False

        return document["column_config_list"]