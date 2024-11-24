# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/7/19
Last Modified: 2023/7/19
Description: 
"""
import datetime


class BaseConfig:
    """通用配置"""
    # JWT-extended
    JWT_SECRET_KEY = "secret_key"
    JWT_ACCESS_TOKEN_EXPIRES_SECONDS = 86400    # 24小时
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRES_SECONDS)
    JWT_TOKEN_LOCATION = ["headers", "cookies", "json", "query_string"]
    JWT_JSON_KEY = "token"
    JWT_REFRESH_JSON_KEY = "token"


class DevConfig(BaseConfig):
    """开发环境配置"""
    DEBUG = True

    # API域名
    CLIENT_DOMAIN = "http://localhost:5000"
    ADMIN_DOMAIN = "http://localhost:5000"
    APP_DOMAIN = "http://localhost:5000"

    # Mongo数据库
    MONGO_URI = "mongodb://localhost:27017/intellifield"
    MONGO_HOST = "localhost"
    MONGO_PORT = 27017


class TestConfig(BaseConfig):
    """测试环境配置"""
    DEBUG = True

    # API域名
    CLIENT_DOMAIN = "https://client.intellifield.cn"
    ADMIN_DOMAIN = "https://admin.intellifield.cn"
    APP_DOMAIN = "https://app.intellifield.cn"

    # Mongo数据库(腾讯云)
    # MONGO_URI = "mongodb://124.221.22.165:27017/intellifield"
    # MONGO_HOST = "124.221.22.165"

    # Mongo数据库(百度云)
    MONGO_URI = "mongodb://192.168.16.2:27017/intellifield"
    MONGO_HOST = "192.168.16.2"
    MONGO_PORT = 27017


class ProConfig(BaseConfig):
    """生产环境配置"""
    DEBUG = False

    # API域名
    CLIENT_DOMAIN = "https://client.intellifield.cn"
    ADMIN_DOMAIN = "https://admin.intellifield.cn"
    APP_DOMAIN = "https://app.intellifield.cn"

    # Mongo数据库(腾讯云)
    # MONGO_URI = "mongodb://124.221.22.165:27017/intellifield"
    # MONGO_HOST = "124.221.22.165"

    # Mongo数据库(百度云)
    # MONGO_URI = "mongodb://120.48.94.222:27017/intellifield"
    # MONGO_HOST = "120.48.94.222"
    MONGO_URI = "mongodb://192.168.16.2:27017/intellifield"
    MONGO_HOST = "192.168.16.2"
    MONGO_PORT = 27017


ConfigMapping = {
    'dev': DevConfig(),
    'test': TestConfig(),
    'pro': ProConfig()
}