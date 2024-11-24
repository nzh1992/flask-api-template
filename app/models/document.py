# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/8
Last Modified: 2023/12/8
Description: 档案模型
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


class Document(BasicModel):
    # 默认6列
    DEFAULT_COLUMNS = ['种子名称', '种子编号', '父本', '母本', '审定', '审定编号']

    def __init__(self, req=None, db=None):
        if db is not None:
            super(Document, self).__init__(db=db)
        else:
            super(Document, self).__init__(req=req)

        self.collection_name = "document"
        self.data_collection_name = "document_data"
        self.excel_collection_name = "document_excel"
        self.land_collection_name = "land"

    def is_exist(self, document_id):
        return super(Document, self).is_exist(self.collection_name, document_id)

    def is_exist_by_name(self, document_name):
        """创建档案时，判断档案名称是否存在"""
        condition = {"document_name": document_name}
        document = self.db[self.collection_name].find_one(condition)
        if document:
            return True

        return False


    def is_exist_on_update(self, document_name):
        """更新档案时，判断档案名称是否存在"""
        condition = {"document_name": document_name}
        count = self.db[self.collection_name].count_documents(condition)
        if count > 1:
            return True

        return False

    def is_seed_exist(self, seed_id):
        return super(Document, self).is_exist(self.data_collection_name, seed_id)

    @staticmethod
    def __get_column_name_type_mapping(column_config_list):
        """
        根据column_config_list，返回列名和列类型映射关系

        :return: dict. {'列名1': '列数据类型', ...}
        """
        mapping = dict(zip(
            [c.get("dataIndex") for c in column_config_list],
            [c.get("dataType") for c in column_config_list]
        ))
        return mapping

    def __compare_column_config_list(self, raw_mapping, new_mapping):
        """
        对比两个列配置对象区别.

        共计4种情况，删除列(delete)、新增列(add)、修改列类型(change_type)。

        :param raw_column_config_list: list.
        :param new_column_config_list: list.
        :return:
        """
        now_dt = DateTime.get_datetime_now_str(custom_format="%Y%m%d%H%M%S")

        # 记录改动内容
        diff_list = []

        for new_name, new_type in new_mapping.items():
            # 1. 默认列不做处理
            if new_name in self.DEFAULT_COLUMNS:
                continue

            if new_name in raw_mapping.keys() and new_type != raw_mapping.get(new_name):
                # 2. 如果改动某一列的类型
                raw_key = f"{new_name}_{raw_mapping.get(new_name)}"
                bak_key = f"{raw_key}_{now_dt}"
                new_key = f"{new_name}_{new_type}"
                diff = {
                    "change_type": {
                        "raw_column": raw_key,
                        "bak_column": bak_key,
                        "new_column": new_key
                    }
                }
                diff_list.append(diff)
            elif new_name not in raw_mapping.keys():
                # 3. 如果是新增(修改列名也被视为新增)
                add_key = f"{new_name}_{new_type}"
                diff = {
                    "add": {
                        "new_column": add_key
                    }
                }
                diff_list.append(diff)

        # 4. 找到被删除的列
        for raw_name, raw_type in raw_mapping.items():
            if raw_name in self.DEFAULT_COLUMNS:
                # 跳过默认列
                continue

            if raw_name not in new_mapping.keys():
                raw_key = f"{raw_name}_{raw_type}"
                new_key = f"{raw_key}_{now_dt}"
                diff = {
                    "delete": {
                        "raw_column": raw_key,
                        "new_column": new_key
                    }
                }
                diff_list.append(diff)

        return diff_list

    def get(self, document_id):
        condition = {"_id": ObjectId(document_id)}
        document = self.db[self.collection_name].find_one(condition)
        return document

    def create(self, data):
        # 档案名称
        document_name = data.get("document_name")
        # 培育周期，开始时间
        start_date = data.get("start_date")
        # 培育周期，结束时间
        end_date = data.get("end_date")
        # 土地id
        land_id = data.get("land_id")
        # 列配置
        column_config_list = data.get("column_config_list")

        document_meta = {
            "document_name": document_name,
            "start_date": start_date,
            "end_date": end_date,
            "land_id": land_id,
            "column_config_list": column_config_list
        }
        document_meta.update(self.get_create_meta())
        result = self.db[self.collection_name].insert_one(document_meta)

        # 修改引用土地状态为"使用中"
        condition = {"_id": ObjectId(land_id)}
        update_data = {"$set": {"status": "USED"}}
        self.db[self.land_collection_name].update_one(condition, update_data)

        return str(result.inserted_id)

    def get_seed_list(self, document_id):
        """
        获取档案中的育种数据列表(数据库的document_data集合)

        :return: [{seed_obj1}, {seed_obj2}]
        """
        seeds = self.db[self.data_collection_name].find({'document_id': document_id})
        return list(seeds)

    def update(self, document_id, data):
        # 获取旧档案数据
        condition = {"_id": ObjectId(document_id)}
        document = self.db[self.collection_name].find_one(condition)
        raw_land_id = document.get("land_id")

        # 更新档案
        update_data = {
            "$set": {
                "document_name": data.get("document_name"),
                "start_date": data.get("start_date"),
                "end_date": data.get("end_date"),
                "land_id": data.get("land_id"),
                "column_config_list": data.get("column_config_list")
            }
        }

        # 更新元信息
        update_meta = self.get_update_meta()
        update_data["$set"].update(update_meta)
        self.db[self.collection_name].update_one(condition, update_data)

        # 如果变更了地图，修改对应土地状态
        new_land_id = data.get("land_id")
        if new_land_id != raw_land_id:
            new_land_condition = {"_id": ObjectId(new_land_id)}
            self.db[self.land_collection_name].update_one(new_land_condition, {"$set": {"status": "USED"}})

            # 检查旧土地是否还有其他档案在引用，如果没有引用，将土地状态置为UNUSED
            raw_land_condition = {"_id": ObjectId(raw_land_id)}
            use_count = self.db[self.document_collection_name].count_documents({"land_id": raw_land_id})
            if use_count == 0:
                self.db[self.land_collection_name].update(raw_land_condition, {"$set": {"status": "UNUSED"}})

        return document_id

    def delete(self, document_id):
        # 查看是否有育种数据
        self.db[self.collection_name].delete_one({'_id': ObjectId(document_id)})

        return document_id

    def query_list(self, page_number, page_size, start_date=None, end_date=None, land_id=None, keyword=None):
        """
        档案列表

        :param page_number: int. 当前页数
        :param page_size: int. 每页数量
        :param start_date: str. 培育周期，开始时间
        :param end_date: str. 培育周期，结束时间
        :param land_id: str. 关联土地id
        :param keyword: str. 关键字（档案名称）
        :return:
        """
        # 查询条件
        condition = {}

        if start_date:
            condition.update({'start_date': {"$gte": start_date}})
        if end_date:
            condition.update({'end_date': {"$lte": end_date}})

        if land_id:
            condition.update({'land_id': land_id})

        if keyword:
            condition.update({'document_name': {'$regex': keyword}})

        start = (page_number - 1) * page_size

        documents = self.db[self.collection_name].find(condition).skip(start).limit(page_size)
        total = self.db[self.collection_name].count_documents(condition)
        document_list = list(documents)

        result = {
            "total": total,
            "list": document_list
        }
        return result

    def change_status(self, document_id, status):
        """
        修改档案状态

        :param document_id: str. 档案id
        :param status: str. 状态枚举值
        :return:
        """
        condition = {"_id": ObjectId(document_id)}
        update_data = {"$set": {"status": status}}
        update_data['$set'].update(self.get_update_meta())
        self.db[self.collection_name].update_one(condition, update_data)

    def get_seed_detail(self, seed_id):
        """
        获取一条档案育种数据

        :param seed_id: str. 种子id
        :return:
        """
        condition = {"_id": ObjectId(seed_id)}
        seed = self.db[self.data_collection_name].find_one(condition)

        document_id = seed.get("document_id")
        document_condition = {"_id": ObjectId(document_id)}
        document = self.db[self.collection_name].find_one(document_condition)

        column_config_list = document.get("column_config_list")

        seed_data = {
            "id": seed_id
        }

        for column_config in column_config_list:
            column_name = column_config.get("dataIndex")
            column_type = column_config.get("dataType")

            if column_name in self.DEFAULT_COLUMNS:
                # 默认列，直接根据列名取值
                seed_data.update({column_name: seed.get(column_name)})
            else:
                # 用户自定义列，拼接取值
                key = f"{column_name}_{column_type}"
                seed_data.update({column_name: seed.get(key)})

        # 添加档案id
        seed_data.update({"document_id": seed.get("document_id")})
        # 添加二维码
        seed_data.update({"二维码": seed.get("二维码")})

        # 添加档案列配置数据
        seed_data.update({"column_config_list": document.get("column_config_list")})

        return seed_data

    def import_excel(self, document_id, excel_id):
        """
        导入excel

        :param document_id: str. 档案id
        :param excel_id: str. excel文件id
        :return:
        """
        # 读取excel文件
        excel = self.db[self.excel_collection_name].find_one({"_id": ObjectId(excel_id)})
        excel_data = excel.get("data")
        excel_filename = excel.get("name")

        # 读取excel
        df = pd.read_excel(excel_data, engine="openpyxl", dtype=str)

        # 填充所有nan为空字符串
        df = df.fillna("")

        # 1.解析列头，作为文档配置中自定义列
        df_headers = list(df.columns)
        column_config_list = []
        for head in df_headers:
            column_config = {
                "dataIndex": head,
                "dataType": "TEXT"
            }
            column_config_list.append(column_config)

        for default_column in self.DEFAULT_COLUMNS:
            default_column_config = {"dataIndex": default_column, "dataType": "DEFAULT"}
            column_config_list.append(default_column_config)

        update_data = {"$set": {"column_config_list": column_config_list}}
        self.db[self.collection_name].update_one({"_id": ObjectId(document_id)}, update_data)

        # 2.将excel数据，根据列规则写入档案的育种列表中
        seed_datas = []
        # 逐行遍历
        for row_idx, row_series in df.iterrows():
            seed_data = {}
            row_data = dict(row_series)
            for k, v in row_data.items():
                if k in self.DEFAULT_COLUMNS:
                    # 2.1 如果列头在默认列中，直接给该列赋值
                    seed_data[k] = v
                else:
                    # 2.2 如果列头不在默认列中，认为是自定义列，且为文本类型
                    key = f"{k}_TEXT"
                    seed_data[key] = v

            # 补全默认列，默认值为空字符串
            for c in self.DEFAULT_COLUMNS:
                if c not in seed_data.keys():
                    seed_data[c] = ""

            # 添加档案信息
            seed_data["document_id"] = document_id
            # 记录excel_id
            seed_data["excel_id"] = excel_id
            seed_data["excel_name"] = excel_filename
            seed_data.update(self.get_create_meta())
            seed_datas.append(seed_data)

        # 3.批量写入
        result = self.db[self.data_collection_name].insert_many(seed_datas)
        seed_ids = [str(i) for i in result.inserted_ids]

        # 生成二维码
        enterprise_id = self.user.get("enterprise_id")
        short_name = f"NZY_{enterprise_id}"
        for seed_id in seed_ids:
            # 二维码data
            qr_code_data = {
                "type": "SEED",
                "enterprise_id": enterprise_id,
                "seed_id": seed_id
            }
            qr_code_data_str = json.dumps(qr_code_data)

            qr_code = QRCode(qr_code_data_str, req=self.req)
            qr_img_id = qr_code.save()
            api_domain = current_app.config['CLIENT_DOMAIN']
            download_url = f"{api_domain}/api/v1/image/?image_id={qr_img_id}&short_name={short_name}"
            # 更新数据库二维码
            self.db[self.data_collection_name].update_one({"_id": ObjectId(seed_id)}, {"$set": {"二维码": download_url}})

    def export_excel(self, document_id):
        """
        导出档案数据

        :param document_id: str. 档案id
        :return:
        """
        document = self.get(document_id)

        # 档案名称作为excel文件名
        excel_name = document.get("name")

        # 获取档案数据
        breeding_list = self.get_breeding_data(document_id).get("breeding_list")
        df = pd.DataFrame(breeding_list)

        # 写入文件
        f_dir = os.path.join(os.getcwd(), "data")
        excel_fp = os.path.join(f_dir, excel_name)

        df.to_excel(excel_fp)

        return excel_fp


    def get_breeding_data(self, document_id, keyword=None):
        """
        获取档案下全部育种数据

        :param document_id: str. 档案id
        :param keyword: str. 关键字（种子名称/种子编号）
        :return:
        """
        document = self.db[self.collection_name].find_one({"_id": ObjectId(document_id)})

        # 1. 档案元信息
        document_name = document.get("name")
        start_date = document.get("start_date")
        end_date = document.get("end_date")
        land = document.get("land_id")
        description = document.get("description")
        column_config_list = document.get("column_config_list")
        import_status = document.get("import_status")

        # 2. 档案数据
        # 查询条件
        condition = {"document_id": document_id}
        if keyword:
            condition.update({
                "$or": [
                    {"种子名称": {"$regex": keyword}},
                    {"种子编号": {"$regex": keyword}}
                ]
            })

        document_datas = self.db[self.data_collection_name].find(condition)

        table_data_list = []
        for document_data in document_datas:
            row_data = dict()
            row_id = str(document_data.get("_id"))
            row_data.update({"id": row_id})

            # 根据列配置决定前端获取哪些列
            for column_config in column_config_list:
                column_name = column_config.get("dataIndex")
                if column_name in self.DEFAULT_COLUMNS:
                    # 2.1 默认6列，直接提取
                    row_data.update({column_name: document_data.get(column_name)})
                else:
                    # 2.2 用户自定义列
                    # 拼接列名，来匹配mongo中文档的key
                    data_index = column_config.get('dataIndex')
                    data_type = column_config.get('dataType')
                    key = f"{data_index}_{data_type}"
                    row_data.update({column_name: document_data.get(key)})

            # 返回二维码
            row_data.update({"二维码": document_data.get("二维码")})

            # 所有配置循环结束，表示一行数据被提取完成
            table_data_list.append(row_data)

        breeding_data = {
            "document": {
                "name": document_name,
                "start_date": start_date,
                "end_date": end_date,
                "land": land,
                "description": description,
                "import_status": import_status
            },
            "column_config_list": column_config_list,
            "breeding_list": table_data_list
        }

        return breeding_data

    def get_breeding_data_pagenation(self, pn, pz, document_id, keyword=None):
        """
        获取档案下育种数据列表(分页，小程序使用)

        :param pn: int. 当前页
        :param pz: int. 每页数量
        :param document_id: str. 档案id
        :param keyword: str. 关键字（种子名称/种子编号）
        :return:
        """
        document = self.db[self.collection_name].find_one({"_id": ObjectId(document_id)})

        # 1. 档案元信息
        column_config_list = document.get("column_config_list")

        # 2. 档案数据
        # 查询条件
        condition = {"document_id": document_id}
        if keyword:
            condition.update({
                "$or": [
                    {"种子名称": {"$regex": keyword}},
                    {"种子编号": {"$regex": keyword}}
                ]
            })

        start = (pn - 1) * pz
        document_datas = self.db[self.data_collection_name].find(condition).skip(start).limit(pz)
        total_count = self.db[self.data_collection_name].count_documents(condition)

        table_data_list = []
        for document_data in document_datas:
            row_data = dict()
            row_id = str(document_data.get("_id"))
            row_data.update({"id": row_id})

            # 根据列配置决定前端获取哪些列
            for column_config in column_config_list:
                column_name = column_config.get("dataIndex")
                if column_name in self.DEFAULT_COLUMNS:
                    # 2.1 默认6列，直接提取
                    row_data.update({column_name: document_data.get(column_name)})
                else:
                    # 2.2 用户自定义列
                    # 拼接列名，来匹配mongo中文档的key
                    data_index = column_config.get('dataIndex')
                    data_type = column_config.get('dataType')
                    key = f"{data_index}_{data_type}"
                    row_data.update({column_name: document_data.get(key)})

            # 返回二维码
            row_data.update({"二维码": document_data.get("二维码")})

            return_row = {
                "id": row_data.get("id"),
                "种子名称": row_data.get("种子名称"),
                "种子编号": row_data.get("种子编号"),
                "二维码": row_data.get("二维码"),
            }

            # 所有配置循环结束，表示一行数据被提取完成
            table_data_list.append(return_row)

        breeding_data = {
            "total": total_count,
            "list": table_data_list
        }

        return breeding_data

    def save_breeding_data(self, document_id, breeding_data):
        """
        保存育种数据（客户端）

        :param document_id: str. 档案id
        :param breeding_data: list. 育种数据
        :return:
        """
        enterprise_id = self.user.get("enterprise_id")
        document = self.db[self.collection_name].find_one({"_id": ObjectId(document_id)})

        # 从档案的列配置中读取'列名'和'数据类型'，并形成映射关系
        column_config_list = document.get("column_config_list")
        column_mapping = self.__get_column_name_type_mapping(column_config_list)

        # 逐行处理
        for row_data in breeding_data:
            row_id = row_data.get("id")

            if row_id:
                # 1. 更新育种数据
                row_obj_id = ObjectId(row_id)
                raw_row_data = self.db[self.data_collection_name].find_one({"_id": row_obj_id})

                # 列数据处理
                for column_name, value in row_data.items():
                    if column_name in self.DEFAULT_COLUMNS:
                        # 1.1 默认列不允许修改，跳过
                        pass
                    else:
                        # 1.2 拼接document_data的key名
                        column_type = column_mapping.get(column_name)
                        key = f"{column_name}_{column_type}"
                        # 注意：修改时在历史数据结构上修改
                        raw_row_data[key] = value

                # 更新数据
                update_row = {"$set": raw_row_data}
                raw_row_data.update(self.get_update_meta())
                self.db[self.data_collection_name].update_one({"_id": row_obj_id}, update_row)
            else:
                # 2. 创建育种数据
                # 列数据处理
                row_data_kvs = [(k, v) for k, v in row_data.items()]
                for column_name, value in row_data_kvs:
                    if column_name in self.DEFAULT_COLUMNS:
                        # 2.1 默认列直接存，不拼接类型
                        pass
                    else:
                        # 2.2 拼接document_data的key名
                        column_type = column_mapping.get(column_name)
                        key = f"{column_name}_{column_type}"
                        # 删除仅有列名的数据
                        row_data.pop(column_name)
                        # 注意：创建时在前端发送的数据结构上修改
                        row_data[key] = value

                # 补充document_id
                row_data.update({"document_id": document_id})
                row_data.update(self.get_create_meta())

                # 新建数据
                result = self.db[self.data_collection_name].insert_one(row_data)
                seed_id = str(result.inserted_id)

                # 生成二维码
                qr_code_data = {
                    "type": "SEED",
                    "enterprise_id": enterprise_id,
                    "seed_id": seed_id
                }
                qr_code_data_str = json.dumps(qr_code_data)
                qr_code = QRCode(qr_code_data_str, req=self.req)
                qr_img_id = qr_code.save()

                # 返回下载url
                enterprise_id = self.user.get("enterprise_id")
                short_name = f"NZY_{enterprise_id}"
                api_domain = current_app.config['CLIENT_DOMAIN']
                download_url = f"{api_domain}/api/v1/image/?image_id={qr_img_id}&short_name={short_name}"

                # 更新种子二维码字段
                update_qrcode = {"$set": {"二维码": download_url}}
                self.db[self.data_collection_name].update_one({"_id": ObjectId(seed_id)}, update_qrcode)

    def save_single_breeding_data(self, document_id, seed_id, seed_data):
        """
        保存一条育种数据（小程序）

        :param document_id: str. 档案id
        :param seed_data: dict. 一条育种数据
        :return:
        """
        document = self.db[self.collection_name].find_one({"_id": ObjectId(document_id)})

        # 从档案的列配置中读取'列名'和'数据类型'，并形成映射关系
        column_config_list = document.get("column_config_list")
        column_mapping = self.__get_column_name_type_mapping(column_config_list)

        # 更新育种数据
        if seed_id:
            update_data = {}

            # 列数据处理
            for column_name, value in seed_data.items():
                if column_name in self.DEFAULT_COLUMNS:
                    # 1.1 默认列
                    update_data[column_name] = value
                else:
                    # 1.2 拼接document_data的key名
                    column_type = column_mapping.get(column_name)
                    key = f"{column_name}_{column_type}"
                    # 注意：修改时在历史数据结构上修改
                    update_data[key] = value

            # 更新数据
            update_data.update(self.get_update_meta())
            update_row = {"$set": update_data}
            seed_obj_id = ObjectId(seed_id)
            self.db[self.data_collection_name].update_one({"_id": seed_obj_id}, update_row)
        else:
            # 新建育种数据
            seed_data_iters = list(seed_data.items())
            # 列数据处理
            for column_name, value in seed_data_iters:
                if column_name in self.DEFAULT_COLUMNS:
                    # 1.1 默认列，直接添加
                    pass
                else:
                    # 1.2 拼接document_data的key名
                    column_type = column_mapping.get(column_name)
                    key = f"{column_name}_{column_type}"
                    # 注意：删除原key，新增带有类型的key
                    seed_data[key] = value
                    seed_data.pop(column_name)

            seed_data['document_id'] = document_id

            # 写入
            result = self.db[self.data_collection_name].insert_one(seed_data)
            inserted_id = str(result.inserted_id)
            enterprise_id = self.req.user.get("enterprise_id")
            self.generate_qr_code(enterprise_id, inserted_id)

    def change_import_status(self, document_id, status):
        """修改导入状态"""
        condition = {"_id": ObjectId(document_id)}
        update_data = {"$set": {"import_status": status}}
        self.db[self.collection_name].update_one(condition, update_data)

    def can_import(self, document_id):
        """
        判断档案是否允许导入

        :param document_id: str. 档案id
        :return: bool.
        """
        condition = {"_id": ObjectId(document_id)}
        document = self.db[self.collection_name].find_one(condition)

        import_status = document.get("import_status")
        if import_status == "UNIMPORT":
            return True

        return False

    def generate_qr_code(self, enterprise_id, seed_id):
        """
        为某一种子生成二维码
        :return:
        """
        # 生成二维码
        qr_code_data = {
            "type": "SEED",
            "enterprise_id": enterprise_id,
            "seed_id": seed_id
        }
        qr_code_data_str = json.dumps(qr_code_data)
        qr_code = QRCode(qr_code_data_str, req=self.req)
        qr_img_id = qr_code.save()

        # 返回下载url
        enterprise_id = self.user.get("enterprise_id")
        short_name = f"NZY_{enterprise_id}"
        api_domain = current_app.config['CLIENT_DOMAIN']
        download_url = f"{api_domain}/api/v1/image/?image_id={qr_img_id}&short_name={short_name}"

        # 更新种子二维码字段
        update_qrcode = {"$set": {"二维码": download_url}}
        self.db[self.data_collection_name].update_one({"_id": ObjectId(seed_id)}, update_qrcode)