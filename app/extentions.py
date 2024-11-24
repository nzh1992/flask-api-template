# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/7
Last Modified: 2023/11/7
Description: 项目扩展
"""
from flask_pymongo import PyMongo


mongo = PyMongo()


def get_mongo_client(host, port):
    from pymongo import MongoClient

    mongodb = MongoClient(host, port)
    return mongodb
