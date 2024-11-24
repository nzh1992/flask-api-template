# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/7/8
Last Modified: 2023/7/8
Description: 
"""
import os
import json
import stat

from flask import Flask

from settings import ConfigMapping
from .extentions import mongo


def register_extentions(app):
    """注册扩展"""
    # 注册flask-restx
    from app.apis import api
    api.init_app(app)

    # 注册flask-pymongo
    mongo.init_app(app)


def init_db_admin_user():
    """
    初始化管理员用户表
    如果管理员用户表中没有账号，默认生成一个账号
    :return:
    """
    admin_user_count = mongo.db.admin_user.count_documents({})
    if admin_user_count == 0:
        admin_user_data = {
            "phone_number": "18888888888",
            "password": "123456",
            "user_name": "管理员"
        }
        print("生成后台管理员账号")
        mongo.db.admin_user.insert_one(admin_user_data)


def init_db_region_info():
    """
    初始化省市区表
    :return:
    """
    # 如果intellifield库中，没有province、city、region表，则执行初始化
    main_db_collections = mongo.db.list_collection_names()
    if "province" in main_db_collections and "city" in main_db_collections and "area" in main_db_collections:
        print("省市区相关表存在，跳过初始化")
        return

    # 读取省市区数据
    # 省市区文件路径
    region_fp = os.path.join(os.getcwd(), "data", "最新县及县以上行政区划代码.txt")
    with open(region_fp, 'r') as f:
        f_data = f.read()
        region_data = json.loads(f_data)

    province_data_list = []
    city_data_list = []
    area_data_list = []

    for province in region_data:
        # 省级数据
        province_data = {
            "name": province.get("name"),
            "code": province.get("code"),
        }
        province_data_list.append(province_data)

        # 市级数据
        citys = province.get("children", [])

        for city in citys:
            city_data = {
                "name": city.get("name"),
                "code": city.get("code"),
                "parent_code": province.get("code")
            }
            city_data_list.append(city_data)

            # 区级数据
            areas = city.get("children", [])
            for area in areas:
                area_data = {
                    "name": area.get("name"),
                    "code": area.get("code"),
                    "parent_code": city.get("code")
                }
                area_data_list.append(area_data)


    # 写入数据库
    mongo.db.province.insert_many(province_data_list)
    mongo.db.city.insert_many(city_data_list)
    mongo.db.area.insert_many(area_data_list)

    print("省市区数据写入完成")


def init_db():
    """初始化数据"""
    # 1. 管理端，后台管理员账号
    init_db_admin_user()

    # 2. 管理端，省市区
    init_db_region_info()


def create_app(env='dev'):
    app = Flask(__name__)

    app.__version__ = "v1.0"

    env_config = ConfigMapping.get(env)
    app.config.from_object(env_config)

    register_extentions(app)

    init_db()

    return app
