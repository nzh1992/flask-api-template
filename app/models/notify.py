# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/12
Last Modified: 2023/12/12
Description: 
"""
from bson import ObjectId

from .basic import BasicModel


class Notify(BasicModel):
    def __init__(self, req=None, db=None):
        if db is not None:
            super(Notify, self).__init__(db=db)
        else:
            super(Notify, self).__init__(req=req)

        self.collection_name = "notify"

    def get(self, notify_id):
        notify = self.db[self.collection_name].find_one({"_id": ObjectId(notify_id)})

        notify_data = {
            "id": str(notify.get("_id")),
            "title": notify.get("title"),
            "content": notify.get("content"),
            "date": notify.get("date"),
            "status": notify.get("status")
        }
        return notify_data

    def get_current(self):
        """
        获取最新一条消息（无论是否已读）
        """
        # 按照时间倒序排列，只拿一条消息
        notifys = self.db[self.collection_name].find({}).sort("date", -1).limit(1)
        notify_list = list(notifys)

        if notify_list:
            notify = notify_list[0]
            notify_data = {
                "id": str(notify.get("_id")),
                "title": notify.get("title"),
                "content": notify.get("content"),
                "date": notify.get("date"),
                "status": notify.get("status")
            }
            return notify_data
        else:
            return None

    def get_unread_count(self):
        condition = {"status": "UNREAD"}
        count = self.db[self.collection_name].count_documents(condition)
        return count

    def read(self, notify_ids):
        for notify_id in notify_ids:
            update_data = {
                "$set": {
                    "status": "READ"
                }
            }
            self.db[self.collection_name].update_one({"_id": ObjectId(notify_id)}, update_data)

    def query_list(self, pn, pz, start_date, end_date, status, keyword):
        # 查询条件
        condition = {}
        if start_date and end_date:
            condition.update(
                {
                    'date': {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            )

        if status:
            condition.update({'status': status})

        if keyword:
            condition.update({'title': {'$regex': keyword}})

        start = (pn - 1) * pz
        notifys = self.db[self.collection_name].find(condition).skip(start).limit(pz)
        total = self.db[self.collection_name].count_documents(condition)

        resp_data = {
            'total': total,
            'list': list(notifys)
        }
        return resp_data
