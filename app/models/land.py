# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/8
Last Modified: 2023/12/8
Description: 
"""
from bson import ObjectId

from .basic import BasicModel
from .region import REGION
from utils.geo import GeoManager


class Land(BasicModel):
    def __init__(self, req=None, db=None):
        if db is not None:
            super(Land, self).__init__(db=db)
        else:
            super(Land, self).__init__(req=req)

        self.collection_name = "land"

    def get(self, land_id):
        """根据土地id，获取土地数据"""
        condition = {"_id": ObjectId(land_id)}
        land = self.db[self.collection_name].find_one(condition)
        return land

    def get_all(self):
        """
        获取全部土地，仅带有id和name
        :return: list. [{'id': 'xxx', 'name': 'xxx'}, ...]
        """
        lands = self.db[self.collection_name].find({})
        land_datas = [{'id': str(l.get("_id")), 'land_name': l.get("land_name")} for l in lands]
        return land_datas

    def get_all_of_location(self):
        """获取所有土地，仅带有id、名称、经纬度"""
        lands = self.db[self.collection_name].find({})
        land_data_list = []
        for land in lands:
            land_data = {
                "id": str(land.get("_id")),
                "name": land.get("name"),
                "longitude": land.get("longitude"),
                "latitude": land.get("latitude")
            }
            land_data_list.append(land_data)

        return land_data_list

    def get_count(self, condition=None):
        if not condition:
            condition = {}

        count = self.db[self.collection_name].count_documents(condition)
        return count

    def is_exist(self, land_id):
        """根据土地id，判断土地是否存在"""
        return super(Land, self).is_exist(self.collection_name, land_id)

    @staticmethod
    def _calculate_geo(full_address):
        """
        根据完整地址计算经纬度

        :param full_address: str. 完整地址
        :return:
        """
        locations = GeoManager().get_geocode(full_address)
        return locations

    def create(self, data):
        """
        创建土地

        :return inserted_id: str. 新创建土地的id
        """
        land_name = data.get("land_name")
        detail_address = data.get("detail_address")
        land_image_url = data.get("land_image_url")
        province_data = data.get("province")
        city_data = data.get("city")
        area_data = data.get("area")
        # 土地默认状态：未使用
        land_status = "UNUSED"

        # 土地名称不可重复
        land = self.db[self.collection_name].find_one({"land_name": land_name})
        if land:
            return False

        land_data = {
            "land_name": land_name,
            "detail_address": detail_address,
            "land_image_url": land_image_url,
            "province_name": province_data.get("name"),
            "province_code": province_data.get("code"),
            "city_name": city_data.get("name"),
            "city_code": city_data.get("code"),
            "area_name": area_data.get("name"),
            "area_code": area_data.get("code"),
            "status": land_status
        }

        land_data.update(self.get_create_meta())

        result = self.db[self.collection_name].insert_one(land_data)
        return str(result.inserted_id)

    def update(self, land_id, data):
        """
        更新土地

        :param id: str. 土地id
        :param data: dict. 待更新数据
        :return:
        """
        land_name = data.get("land_name")
        detail_address = data.get("detail_address")
        land_image_url = data.get("land_image_url")
        province = data.get("province")
        city = data.get("city")
        area = data.get("area")

        # 土地名称不可重复
        land_count = self.db[self.collection_name].count_documents({"land_name": land_name})
        if land_count > 1:
            return False

        update_data = {
            "$set": {
                "land_name": land_name,
                "detail_address": detail_address,
                "land_image_url": land_image_url,
                "province_name": province.get("name"),
                "province_code": province.get("code"),
                "city_name": city.get("name"),
                "city_code": city.get("code"),
                "area_name": area.get("name"),
                "area_code": area.get("code")
            }
        }

        update_data['$set'].update(self.get_update_meta())

        self.db[self.collection_name].update_one({'_id': ObjectId(land_id)}, update_data)
        return land_id

    def delete(self, land_id):
        """
        删除土地

        :param land_id: str. 土地id
        :return:
        """
        self.db[self.collection_name].delete_one({'_id': ObjectId(land_id)})

    def query_list(self, page_number, page_size, province_code=None, city_code=None, area_code=None,
                   status=None, keyword=None):
        """
        列表查询

        :param page_number: int. 当前页数
        :param page_size: int. 每页数据量
        :param province_code: str. 省编码
        :param city_code: str. 市编码
        :param area_code: str. 区县编码
        :param status: str. 土地状态
        :param keyword: str. 关键字(土地名称)
        :return: dict. {'total': 当前条件查询出的总数, 'list': 当前页的数据列表}
        """
        condition = {}

        if province_code:
            condition.update({'province_code': province_code})
        if city_code:
            condition.update({'city_code': city_code})
        if area_code:
            condition.update({'area_code': area_code})

        if status:
            condition.update({'status': status})

        if keyword:
            condition.update({'land_name': {'$regex': keyword}})

        # 当前列表土地
        start = (page_number - 1) * page_size
        lands = self.db[self.collection_name].find(condition).skip(start).limit(page_size)

        # 符合筛选条件的土地数量
        total = self.db[self.collection_name].count_documents(condition)

        list_data = {
            "total": total,
            "list": list(lands)
        }
        return list_data
