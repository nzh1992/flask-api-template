# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/8
Last Modified: 2023/12/8
Description: 
"""
from .basic import BasicModel


class Banner(BasicModel):
    """
    微信小程序的轮播图设置
    """
    def __init__(self, req=None, db=None):
        if db is not None:
            super(Banner, self).__init__(db=db)
        else:
            super(Banner, self).__init__(req=req)

        self.collection_name = "banner"

    def init_data(self):
        """
        在程序运行时初始化数据
        """
        count = self.db[self.collection_name].count_documents({})
        if count == 0:
            # banner默认数据
            banner_data = {
                "autoplay": False,      # 是否自动播放
                "interval": 0,          # 播讲间隔（秒）
                "banner_list": []       # 轮播图url列表
            }
            self.db[self.collection_name].insert_one(banner_data)

    def get(self):
        # 有且只有一条数据
        banner = self.db[self.collection_name].find_one({})
        return banner

    def update(self, data):
        autoplay = data.get("autoplay")
        interval = data.get("interval")
        banner_list = data.get("banner_list")

        # 有且只有一条数据
        banner = self.db[self.collection_name].find_one({})
        obj_id = banner.get("_id")

        update_data = {
            "$set": {
                "autoplay": autoplay,
                "interval": interval,
                "banner_list": banner_list
            }
        }
        update_data["$set"].update(self.get_update_meta())
        self.db[self.collection_name].update_one({"_id": obj_id}, update_data)