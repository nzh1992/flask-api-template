# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/23
Last Modified: 2023/11/23
Description: 地理
"""
import json
import requests


class GeoManager:
    """
    地图工具类，调用高德开发者平台服务。
    """
    def __init__(self):
        # 高德开发者平台-应用-key
        self.key = "be76ee6b37a5c03fb0c45bac9bad2484"
        # 获取地理编码API
        self.geocode_api = "https://restapi.amap.com/v3/geocode/geo"

    def get_geocode(self, address):
        """
        根据指定地址获取经纬度坐标。
        :param address: str. 地址
        :return:
        """
        params = {
            "key": self.key,
            "address": address
        }

        resp = requests.get(self.geocode_api, params=params)
        resp_data = json.loads(resp.content)

        # 根据infocode判定API是否调用成功
        if resp_data.get("infocode") != "10000":
            raise Exception(f"获取经纬度API调用失败，{resp_data.get('info')}")

        location_str = resp_data.get('geocodes')[0].get('location')
        location = location_str.split(",")
        return location


if __name__ == '__main__':
    add = "北京市朝阳区阜通东大街6号"
    location = GeoManager().get_geocode(add)
    print(location)