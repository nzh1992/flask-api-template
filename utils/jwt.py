# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/4/24
Last Modified: 2023/4/24
Description: 
"""
import time
import datetime
from functools import wraps

import jwt
from jwt.exceptions import PyJWTError
from bson import ObjectId
from flask import current_app

from utils.response import ResponseMaker
from app.extentions import mongo
from utils.mongo import Mongo
from utils.dt import DateTime


class JWTUtil:
    token_expire_time = 3600 * 12       # token过期时间，12小时
    secret = 'secret'                   # 秘钥
    algorithm = 'HS256'                 # 加密算法

    @classmethod
    def create_token(cls, user_id):
        """
        创建token

        :param user_id: int. 用户id
        """
        # 当前UTC时间戳
        utc_timestamp = time.mktime(datetime.datetime.utcnow().utctimetuple())
        # 过期UTC时间戳(秒)
        utc_expire_time = utc_timestamp + cls.token_expire_time
        # 秒转为毫秒
        utc_expire_time_ms = utc_expire_time * 1000

        payload = {
            'id': user_id,
            'token_expires': utc_expire_time_ms
        }
        token = jwt.encode(payload, cls.secret, algorithm=cls.algorithm)

        payload.update({'access_token': token})

        return payload

    @classmethod
    def verify_token(cls, token):
        """
        检查token是否合法（函数调用）

        :param token: str.
        :return: 返回值中code为枚举值，0成功，1token错误，2token过期
        """
        try:
            # 如果token中不含有“Bearer”, 报错
            if "Bearer" not in token:
                return {'result': False, 'msg': "Token格式错误", "code": 1}

            # 参数token格式: "Bearer {token}"，所以需要获取原始token
            raw_token = token.split('Bearer ')[1]

            # 解析token
            payload = jwt.decode(raw_token, cls.secret, algorithms=[cls.algorithm])
        except PyJWTError:
            return {'result': False, 'msg': "Token解析失败", "code": 1}

        # 校验过期时间
        token_expires = payload.get("token_expires")
        current_utc_timestamp = time.mktime(datetime.datetime.utcnow().utctimetuple())
        if current_utc_timestamp > token_expires:
            return {'result': False, 'msg': "Token过期", 'code': 2}

        return {'result': True, 'msg': "Token合法", 'id': payload.get('id'), 'code': 0}

    @classmethod
    def verify_token_decorator(cls, request):
        """
        检查token是否合法（装饰器调用）
        """
        def decorated(func):

            @wraps(func)
            def wrapper(*args, **kwargs):
                token = request.headers.get("Authorization")

                # 如果header中没有，再到查询参数中找
                if not token:
                    token = request.args.get("Authorization")

                # 如果查询参数中也没有，报错处理
                if not token:
                    return ResponseMaker.token_missing()

                try:
                    result = cls.verify_token(token)

                    if result.get("code") == 1:
                        return ResponseMaker.token_error()
                    elif result.get("code") == 2:
                        return ResponseMaker.token_expire()
                    elif result.get("code") == 0:
                        # 获取用户信息
                        user_id = ObjectId(result.get("id"))
                        user = mongo.db.user.find_one({"_id": user_id})
                        has_company = True
                        if not user:
                            # 如果企业用户查不到，表示是系统用户
                            has_company = False
                            user = mongo.db.admin_user.find_one({"_id": user_id})

                        if not user:
                            # 还是没有用户，说明用户id错误或用户被删除
                            raise Exception("用户id错误或用户被删除")

                        request.user = user

                        if has_company:
                            enterprise_id = user.get("enterprise_id")
                            enterprise = mongo.db.enterprise.find_one({"_id": ObjectId(enterprise_id)})
                            db_name = enterprise.get("db_name")

                            # 检查企业状态
                            if enterprise.get("status") != "ENABLE":
                                return ResponseMaker.enterprise_disable()

                            # 检查企业是否被删除
                            if enterprise.get("is_delete") is True:
                                return ResponseMaker.enterprise_deleted()

                            # 检查企业授权周期
                            current_dt = DateTime.get_datetime_now()
                            start_dt = datetime.datetime.strptime(enterprise.get("start_date"), "%Y-%m-%d")
                            end_dt = datetime.datetime.strptime(enterprise.get("end_date"), "%Y-%m-%d")
                            if current_dt < start_dt or current_dt > end_dt:
                                return ResponseMaker.enterprise_authorization_deprecated()

                            # 对应数据库连接
                            host = current_app.config["MONGO_HOST"]
                            port = current_app.config["MONGO_PORT"]
                            db = Mongo(host, port)
                            request.db = db.get_db_by_name(db_name)

                    return func(args, kwargs)
                except jwt.ExpiredSignatureError as e:
                    raise e
                except Exception as e:
                    raise e

                return result

            return wrapper

        return decorated
