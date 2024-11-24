# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/8
Last Modified: 2023/12/8
Description: 所有模型类的基础类，通过此类提供最基础的功能
"""
from bson import ObjectId

from app.extentions import mongo
from utils.dt import DateTime


class BasicModel:
    def __init__(self, *args, **kwargs):
        """
        BasicModel提供数据库连接，以及模型的通用功能。

        关键字参数有两个："req" 和 "db"
            - req: flask.request. flask中的请求对象。
                在收到请求时，request会根据token挂载user对象和db对象。
            - db: utils.mongo.Mongo(host, port).get_db(). mongo数据库对象

        说明：
            req和db参数，只会有一个生效，优先使用db，若未提供db，则使用req。

        不同场景用法：
            1. 当在请求头中带有Authorization字段时，可以从token中解析出数据库连接
            通过req对象的db属性获取数据连接

            2. 当API不需要请求头时，例如预览图片、预览视频
            通过mongo数据库对象连接

            3. 直接在后台调用模型对象时，例如创建公司时初始化banner
            通过mongo数据库对象连接

            4. 请求(flask.reqeust)中没有db对象时，用默认数据库连接
        """
        if "db" in kwargs:
            self.db = kwargs.get("db")
            if kwargs.get("req"):
                self.user = kwargs.get("req").user
        else:
            req = kwargs.get("req")
            self.req = req

            if hasattr(req, "db"):
                self.db = req.db
            else:
                self.db = mongo.db

            self.user = req.user

    @staticmethod
    def is_id_format_right(id):
        """
        检查id格式是否正确
        """
        try:
            ObjectId(id)
        except Exception as e:
            return False
        else:
            return True

    def is_exist(self, collection_name, id):
        condition = {"_id": ObjectId(id)}
        obj = self.db[collection_name].find_one(condition)
        if not obj:
            return False

        return True

    def get_create_meta(self):
        """
        获取创建时元数据

        元数据有4个字段：
            - create_user_id: str. 创建人id
            - update_user_id: str. 修改人id
            - create_time: str. 创建时间
            - update_time: str. 修改时间

        :return: dict.
        """
        if self.user is not None:
            current_dt = DateTime.get_datetime_now_str()

            meta_data = {
                "create_user_id": str(self.user.get("_id")),
                "create_time": current_dt,
                "update_user_id": str(self.user.get("_id")),
                "update_time": current_dt
            }
            return meta_data
        else:
            return {}

    def get_update_meta(self):
        if self.user is not None:
            current_dt = DateTime.get_datetime_now_str()

            meta_data = {
                "update_user_id": str(self.user.get("_id")),
                "update_time": current_dt
            }
            return meta_data
        else:
            return {}
