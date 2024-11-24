# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/9
Last Modified: 2023/12/9
Description: 种子模型
"""
from bson import ObjectId

from .basic import BasicModel


class Seed(BasicModel):
    # 默认6列
    DEFAULT_COLUMNS = ['种子名称', '种子编号', '父本', '母本', '审定', '审定编号']

    def __init__(self, req=None, db=None):
        if db is not None:
            super(Seed, self).__init__(db=db)
        else:
            super(Seed, self).__init__(req=req)

        self.collection_name = "seed"
        self.stash_collection_name = "stash"
        self.document_data_collection_name = "document_data"

    def __get_all_stash_inventory_dict(self):
        """
        获取所有仓库中的种子和种子信息的映射

        :return: dict.
            {
                'stash_id': {
                    'seed_id': {object of inventory_list}
                }
            }
        """
        stash_mapping = {}
        stashes = list(self.db[self.stash_collection_name].find({}))

        for stash in stashes:
            stash_id = str(stash.get("_id"))
            stash_name = stash.get("name")
            stash_mapping[stash_id] = {}

            inventory_list = stash.get("inventory_list")

            for seed in inventory_list:
                seed_id = seed.get("seed_id")

                # 在种子信息中，挂载仓库信息，避免多次查询
                seed["stash_id"] = stash_id
                seed["stash_name"] = stash_name

                if seed_id in stash_mapping[stash_id].keys():
                    # 如果同一种子在仓库出现多次，将种子数量和重量累加
                    quantity = seed.get("quantity")
                    stash_mapping[stash_id][seed_id]["quantity"] += quantity
                    weight = seed.get("weight")
                    stash_mapping[stash_id][seed_id]["weight"] += weight
                else:
                    stash_mapping[stash_id][seed_id] = seed

        return stash_mapping

    def __get_stash_info_mapping(self):
        """获取key为仓库id，value为仓库信息的字典"""
        all_stash = self.db[self.stash_collection_name].find({})
        stash_id_mapping = {}
        for stash in all_stash:
            stash_id = str(stash.get("_id"))
            stash_info = {"id": stash_id, "name": stash.get("name")}
            stash_id_mapping[stash_id] = stash_info

        return stash_id_mapping

    def is_exist(self, seed_id):
        return super(Seed, self).is_exist(self.collection_name, seed_id)

    def create(self, data):
        name = data.get("种子名称")
        code = data.get("种子编号")
        paternal = data.get("父本")
        maternal = data.get("母本")
        is_approve = True if data.get("审定") else False
        approve_code = data.get("审定编号")

        # 由种子列表创建的,来源为"创建"
        source = "CREATE"

        seed_data = {
            "种子名称": name,
            "种子编号": code,
            "父本": paternal,
            "母本": maternal,
            "审定": is_approve,
            "审定编号": approve_code,
            "source": source
        }
        seed_data.update(self.get_create_meta())
        self.db[self.collection_name].insert_one(seed_data)

    def get(self, seed_id):
        condition = {"_id": ObjectId(seed_id)}
        return self.db[self.collection_name].find_one(condition)

    def get_all(self):
        seeds = self.db[self.collection_name].find({})

        # 1.种子列表
        seed_data_list = []
        for seed in seeds:
            seed_data = {
                "id": str(seed.get("_id")),
                "种子名称": seed.get("种子名称"),
                "种子编号": seed.get("种子编号")
            }
            seed_data_list.append(seed_data)

        # 2.档案种子
        document_seed_datas = []
        document_seeds = self.db[self.document_data_collection_name].find({})

        for seed in document_seeds:
            seed_id = str(seed.get("_id"))
            seed_data = {
                "id": seed_id,
                "种子名称": seed.get("种子名称"),
                "种子编号": seed.get("种子编号")
            }
            document_seed_datas.append(seed_data)

        # 合并
        seed_data_list.extend(document_seed_datas)

        return seed_data_list

    def get_count(self, condition=None):
        if not condition:
            condition = {}

        count = self.db[self.collection_name].count_documents(condition)
        return count

    def get_name_by_id(self, seed_id):
        """
        根据种子id获取种子名称，如果seed_id=None，返回None。否则返回种子名称

        :param seed_id:
        :return:
        """
        if seed_id:
            seed = self.db[self.collection_name].find_one({"_id": ObjectId(seed_id)})
            seed_name = seed.get("种子名称")
        else:
            seed_name = None

        return seed_name

    def update(self, seed_id, data):
        name = data.get("种子名称")
        code = data.get("种子编号")
        paternal = data.get("父本")
        maternal = data.get("母本")
        is_approve = True if data.get("审定") else False
        approve_code = data.get("审定编号")

        seed_data = {
            "$set": {
                "种子名称": name,
                "种子编号": code,
                "父本": paternal,
                "母本": maternal,
                "审定": is_approve,
                "审定编号": approve_code,
            }
        }
        seed_data['$set'].update(self.get_update_meta())

        self.db[self.collection_name].update_one({"_id": ObjectId(seed_id)}, seed_data)

    def delete(self, seed_id):
        self.db[self.collection_name].delete_one({'_id': ObjectId(seed_id)})

    def query_list(self, pn, pz, source, is_approve, q_stash_id, keyword):
        """
        查询种子列表

        :param pn: int. 当前页数
        :param pz: int. 每页数量
        :param source: str. 数据源。枚举字符串，'CREATE'/'DOCUMENT'
        :param is_approve: bool. 审定
        :param q_stash_id: str. 仓库id
        :param keyword: str. 关键字（种子名称/种子编号）
        :return:
        """
        # 1.种子列表数据
        # 加载所有种子
        seeds = list(self.db[self.collection_name].find({}))

        # 仓库中的种子id-仓库信息映射
        stash_mapping = self.__get_all_stash_inventory_dict()

        # 所有仓库
        stash_info_mapping = self.__get_stash_info_mapping()

        seed_list = []
        for seed in seeds:
            # 种子基础信息
            seed_id = str(seed.get("_id"))
            seed_data = {
                "id": seed_id,
                "种子名称": seed.get("种子名称"),
                "种子编号": seed.get("种子编号"),
                "父本": self.get_name_by_id(seed.get("父本")),
                "母本": self.get_name_by_id(seed.get("母本")),
                "审定": seed.get("审定"),
                "审定编号": seed.get("审定编号"),
                "source": seed.get("source"),
                "total_quantity": 0,
                "total_weight": 0,
                "stash_list": []
            }

            # 遍历仓库信息
            for stash_id, seed_dict in stash_mapping.items():
                if seed_id in seed_dict.keys():
                    # 如果再仓库中，将仓库信息加入
                    stash_info = {
                        "id": stash_info_mapping.get(stash_id).get("id"),
                        "name": stash_info_mapping.get(stash_id).get("name")
                    }
                    seed_data["stash_list"].append(stash_info)
                    # 获取仓库种子映射
                    stash_seed_dict = seed_dict.get(seed_id)
                    # 累加数量
                    seed_data["total_quantity"] += stash_seed_dict.get("quantity") if stash_seed_dict else 0
                    # 累加重量
                    seed_data["total_weight"] += stash_seed_dict.get("weight") if stash_seed_dict else 0

            seed_list.append(seed_data)

        # 2.档案种子
        document_seed_datas = []
        document_seeds = self.db[self.document_data_collection_name].find({})

        for seed in document_seeds:
            seed_id = str(seed.get("_id"))
            seed_data = {
                "id": seed_id,
                "种子名称": seed.get("种子名称"),
                "种子编号": seed.get("种子编号"),
                "父本": self.get_name_by_id(seed.get("父本")),
                "母本": self.get_name_by_id(seed.get("母本")),
                "审定": seed.get("审定"),
                "审定编号": seed.get("审定编号"),
                "source": "DOCUMENT",
                "stash_list": [],
                "total_quantity": 0,
                "total_weight": 0
            }
            document_seed_datas.append(seed_data)

        # 3. 合并"种子列表"和"档案育种列表"
        seed_list.extend(document_seed_datas)

        # 4. 过滤条件
        if source:
            seed_list = list(filter(lambda x: x["source"] == source, seed_list))

        if is_approve is not None:
            seed_list = list(filter(lambda x: x["审定"] == is_approve, seed_list))

        if q_stash_id:
            seed_list = list(filter(lambda x: stash_id in [i.get("id") for i in x["stash_list"]], seed_list))

        if keyword:
            seed_list = list(filter(lambda x: keyword in x["种子名称"] or keyword in x["种子编号"], seed_list))

        start = (pn - 1) * pz
        end = start + pz
        resp_data = {
            'total': len(seed_list),
            'list': seed_list[start: end]
        }

        return resp_data

    def wx_query_list(self, pn, pz, source, keyword):
        """
        查询种子列表

        :param pn: int. 当前页数
        :param pz: int. 每页数量
        :param source: str. 数据源。枚举字符串，'CREATE'/'DOCUMENT'
        :param is_approve: bool. 审定
        :param q_stash_id: str. 仓库id
        :param keyword: str. 关键字（种子名称/种子编号）
        :return:
        """
        # 1.种子列表数据
        # 加载所有种子
        seeds = list(self.db[self.collection_name].find({}))

        seed_list = []
        for seed in seeds:
            # 种子基础信息
            seed_id = str(seed.get("_id"))
            seed_data = {
                "id": seed_id,
                "source": seed.get("source"),
                "种子名称": seed.get("种子名称"),
                "种子编号": seed.get("种子编号")
            }
            seed_list.append(seed_data)

        # 2.档案种子
        document_seed_datas = []
        document_seeds = self.db[self.document_data_collection_name].find({})

        for seed in document_seeds:
            seed_id = str(seed.get("_id"))
            seed_data = {
                "id": seed_id,
                "source": "DOCUMENT",
                "种子名称": seed.get("种子名称"),
                "种子编号": seed.get("种子编号")
            }
            document_seed_datas.append(seed_data)

        # 3. 合并"种子列表"和"档案育种列表"
        seed_list.extend(document_seed_datas)

        # 4. 过滤条件
        if source:
            seed_list = list(filter(lambda x: x["source"] == source, seed_list))

        if keyword:
            seed_list = list(filter(lambda x: keyword in x["种子名称"] or keyword in x["种子编号"], seed_list))

        start = (pn - 1) * pz
        end = start + pz
        resp_data = {
            'total': len(seed_list),
            'list': seed_list[start: end]
        }

        return resp_data

    def name_count(self, name):
        """种子名称的数量"""
        name_condition = {"种子名称": name}
        name_count = self.db[self.collection_name].count_documents(name_condition)

        return name_count

    def code_count(self, code):
        """种子编号的数量"""
        code_condition = {"种子编号": code}
        code_count = self.db[self.collection_name].count_documents(code_condition)

        return code_count

    def has_ref(self, seed_id):
        """
        检查种子是否被引用

        1. 检查种子列表中的父本或母本
        2. 检查档案种子数据中父本或母本
        :return: list. 如果ref_list为空表示没有引用。
        """
        ref_list = []

        # 检查种子列表中的父本
        seed_condition = {"父本": seed_id}
        seed = self.db[self.collection_name].find_one(seed_condition)
        if seed:
            ref_list.append(f"正在被{seed.get('种子名称')}作为父本使用")

        # 检查种子列表中的母本
        seed_condition = {"母本": seed_id}
        seed = self.db[self.collection_name].find_one(seed_condition)
        if seed:
            ref_list.append(f"正在被{seed.get('种子名称')}作为母本使用")

        return ref_list
