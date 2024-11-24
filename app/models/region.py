# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/8
Last Modified: 2023/12/8
Description: 
"""
import os
import json


class Region:
    """
    省市区

    注意：作为单例对象引用。
    """
    def __init__(self):
        # 省市区数据文件路径
        self.data_fp = os.path.join(os.getcwd(), "data", "最新县及县以上行政区划代码.txt")

        # 加载数据到内存
        with open(self.data_fp, 'r') as f:
            f_data = f.read()
            self.region_data = json.loads(f_data)

    def code_to_name(self, code_list):
        """
        将一组省市区code转换为省市区name

        :param code_list: list. 一共三个元素，其中每个元素是code字符串。
        :return:
        """
        if not isinstance(code_list, list):
            raise Exception("code_list必须是list对象")

        if len(code_list) != 3:
            raise Exception("code_list中只能有三个元素，分别表示省市区code")

        province_code, city_code, area_code = code_list

        for province_data in self.region_data:
            if province_data.get("code") == province_code:
                province_name = province_data.get("name")
                citys = province_data.get("children")

                for city in citys:
                    if city.get("code") == city_code:
                        city_name = city.get("name")
                        areas = city.get("children")

                        for area in areas:
                            if area.get("code") == area_code:
                                area_name = area.get("name")

        return province_name, city_name, area_name


# 作为单例调用
REGION = Region()
