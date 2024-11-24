# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/9
Last Modified: 2023/12/9
Description: 仓库模型
"""
from bson import ObjectId

from .basic import BasicModel


class Stash(BasicModel):
    def __init__(self, req=None, db=None):
        if db is not None:
            super(Stash, self).__init__(db=db)
        else:
            super(Stash, self).__init__(req=req)

        self.collection_name = "stash"
        self.seed_collection_name = "seed"

    def is_exist(self, stash_id):
        return super(Stash, self).is_exist(self.collection_name, stash_id)

    def get(self, stash_id):
        condition = {"_id": ObjectId(stash_id)}
        return self.db[self.collection_name].find_one(condition)

    def get_all(self):
        stashes = self.db[self.collection_name].find({})
        stash_list = [{"id": str(s.get("_id")), "name": s.get("name")} for s in stashes]
        return stash_list

    def get_inventory_dict(self, stash_id):
        """
        获取某一仓库中的种子和种子信息的映射

        :param stash_id: str. 仓库id
        :return: dict. {'seed_id': {seed}, ...}
        """
        condition = {"_id": ObjectId(stash_id)}
        stash = self.db[self.collection_name].find_one(condition)

        inventory_list = stash.get("inventory_list")

        seed_mapping = {}
        for seed_info in inventory_list:
            seed_id = seed_info.get("seed_id")
            seed_mapping[seed_id] = seed_info

        return seed_mapping

    def create(self, data):
        name = data.get("name")
        region = data.get("region")
        detail_address = data.get("detail_address")
        description = data.get("description")
        # 种子列表
        inventory_list = data.get("inventory_list")
        # 创建仓库时的默认状态，ENABLE
        status = "ENABLE"

        if region:
            province_code, city_code, area_code = region
        else:
            province_code, city_code, area_code = None

        # 校验'种子列表'
        # 如果前端没传quantity和weight，默认值为0
        for inventory in inventory_list:
            if not inventory.get("quantity"):
                inventory["quantity"] = 0

            if not inventory.get("weight"):
                inventory["weight"] = 0

        stash_data = {
            "name": name,
            "province_code": province_code,
            "city_code": city_code,
            "area_code": area_code,
            "detail_address": detail_address,
            "description": description,
            "inventory_list": inventory_list,
            "status": status
        }
        stash_data.update(self.get_create_meta())
        self.db[self.collection_name].insert_one(stash_data)

    def update(self, stash_id, data):
        name = data.get("name")
        region = data.get("region")
        detail_address = data.get("detail_address")
        description = data.get("description")
        inventory_list = data.get("inventory_list")  # 种子列表

        if region:
            province_code, city_code, area_code = region
        else:
            province_code, city_code, area_code = None

        # 校验'种子列表'
        # 如果前端没传quantity和weight，默认值为0
        for inventory in inventory_list:
            if not inventory.get("quantity"):
                inventory["quantity"] = 0

            if not inventory.get("weight"):
                inventory["weight"] = 0

        stash_data = {
            "$set": {
                "name": name,
                "province_code": province_code,
                "city_code": city_code,
                "area_code": area_code,
                "detail_address": detail_address,
                "description": description,
                "inventory_list": inventory_list,
            }
        }
        stash_data['$set'].update(self.get_update_meta())
        self.db[self.collection_name].update_one({"_id": ObjectId(stash_id)}, stash_data)

    def delete(self, stash_id):
        condition = {"_id": ObjectId(stash_id)}
        self.db[self.collection_name].delete_one(condition)

    def query_list(self, pn, pz, status, region, keyword):
        condition = {}

        if status:
            condition.update({'status': status})

        if region:
            province_code, city_code, area_code = region
            condition.update({
                "province_code": province_code,
                "city_code": city_code,
                "area_code": area_code
            })

        if keyword:
            condition.update({"name": {"$regex": keyword}})

        start = (pn - 1) * pz

        stashs = self.db[self.collection_name].find(condition).skip(start).limit(pz)
        total = self.db[self.collection_name].count_documents(condition)

        resp_data = {
            "total": total,
            "list": list(stashs)
        }
        return resp_data

    def seed_list(self, pn, pz, stash_id, keyword):
        """仓库种子列表"""
        condition = {}

        if stash_id:
            condition.update({'_id': ObjectId(stash_id)})

        stash = self.db[self.collection_name].find_one(condition)
        inventory_list = stash.get("inventory_list")

        # 将种子列表中seed_id替换成"种子名称"
        for seed in inventory_list:
            seed_id = seed.pop("seed_id")
            seed_obj = self.db[self.seed_collection_name].find_one({"_id": ObjectId(seed_id)})
            seed["种子名称"] = seed_obj.get("种子名称")
            seed["种子编号"] = seed_obj.get("种子编号")

        # 根据keyword筛选
        if keyword:
            seed_list = []
            for seed in inventory_list:
                if keyword in seed.get("种子名称") or keyword in seed.get("种子编号"):
                    seed_list.append(seed)

            inventory_list = seed_list

        # 种子数量
        seed_total = len(inventory_list)

        # 分页返回种子数量
        start = (pn - 1) * pz
        end = pn * pz
        seed_list = inventory_list[start: end]

        resp_data = {
            "total": seed_total,
            "list": seed_list
        }
        return resp_data

    def change_status(self, stash_id, status):
        condition = {"_id": ObjectId(stash_id)}
        update_data = {"$set": {"status": status}}
        self.db[self.collection_name].update_one(condition, update_data)