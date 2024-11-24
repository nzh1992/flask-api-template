# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/11
Last Modified: 2023/12/11
Description: 日志工具类
"""
import traceback
from functools import wraps
from enum import Enum

from utils.jwt import JWTUtil
from app.models.log import RequestLogModel
from utils.dt import DateTime


class ClientTypeEnum(Enum):
    """客户端类型枚举"""
    CLIENT = "client"
    APP = "app"
    ADMIN = "admin"


class RequestLogUtil:
    """请求日志工具类"""
    @staticmethod
    def __get_client_type(url):
        """
        通过url区分客户端类型

        本地判断规则：
            url中包含关键字

        服务器上判断规则：
            url中的域名
        """
        # 本地
        if "admin_api" in url:
            return "admin"

        if "app_api" in url:
            return "app"

        if "client_api" in url:
            return "client"

        # 服务器上
        if url.startswith("https://admin"):
            return "admin"

        if url.startswith("https://app"):
            return "app"

        if url.startswith("https://client"):
            return "client"

        return None

    @staticmethod
    def __make_log_data(**kwargs):
        """
        根据参数创建日志内容.（收到请求时记录）

        关键字如下：
            - client_type: str. 客户端类型，枚举字符串。“client”客户端, "app"移动端, "admin"管理端。
            - ip_address: str. 发起请求IP地址
            - user_id: str. 用户id
            - url: str. 完整请求地址
            - http_method: str. HTTP方法
            - header: dict. 请求头
            - params: dict. 查询参数
            - body: dict. 请求体参数
            - start_time: str. 收到请求时间
        """
        log_data = {}

        # 客户端类型
        if "client_type" in kwargs:
            log_data['client_type'] = kwargs.get("client_type")

        # ip地址
        if "ip_address" in kwargs:
            log_data['ip_address'] = kwargs.get("ip_address")

        # 用户id
        if "user_id" in kwargs:
            log_data['user_id'] = kwargs.get("user_id")

        # 完整的请求地址
        if "url" in kwargs:
            log_data['url'] = kwargs.get("url")

        # http方法
        if "http_method" in kwargs:
            log_data['http_method'] = kwargs.get("http_method")

        # 请求头
        if "header" in kwargs:
            log_data['header'] = kwargs.get("header")

        # 查询参数
        if "params" in kwargs:
            log_data['params'] = kwargs.get("params")

        # 请求体参数
        if "body" in kwargs:
            log_data['body'] = kwargs.get("body")

        # 收到请求时间
        if "start_time" in kwargs:
            log_data['start_time'] = kwargs.get("start_time")

        return log_data

    @staticmethod
    def __make_update_log_data(**kwargs):
        """
        根据参数更新日志内容。（请求完成时更新）

        关键字如下：
            - end_time: str. 处理完成时间
            - is_success: bool. 是否成功。所有逻辑正常的记录，值为True，否则为False。
            - msg: str. 如果成功，值为"成功"；如果是已知异常，值为异常描述；如果是未知异常，值为“未知错误”。
            - traceback: str. 异常堆栈信息。只有未知异常才有值，其他情况为None。
            - return_data: any. 请求返回值
        """
        update_log_data = {}

        # 请求头
        if "end_time" in kwargs:
            update_log_data['end_time'] = kwargs.get("end_time")

        # 查询参数
        if "is_success" in kwargs:
            update_log_data['is_success'] = kwargs.get("is_success")

        # 请求体参数
        if "msg" in kwargs:
            update_log_data['msg'] = kwargs.get("msg")

        # 收到请求时间
        if "traceback" in kwargs:
            update_log_data['traceback'] = kwargs.get("traceback")

        # 请求返回值
        if "return_data" in kwargs:
            update_log_data['return_data'] = kwargs.get("return_data")

        return update_log_data

    @classmethod
    def log(cls, request):
        """
        记录日志（装饰器调用）
        """
        def decorated(func):

            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    # client_type
                    client_type = cls.__get_client_type(request.url)
                    # IP地址
                    ip_address = request.remote_addr
                    # 用户id
                    token = request.headers.environ.get('HTTP_AUTHORIZATION')
                    check_reuslt= JWTUtil.verify_token(token)
                    user_id = check_reuslt.get("id")
                    # url
                    url = request.url
                    # http方法
                    http_method = request.method
                    # header
                    header = {
                        "Authorization": token
                    }
                    # params
                    params = dict(request.args)
                    # body
                    if request.mimetype == "application/json":
                        body = request.get_json() if request.data else {}
                    else:
                        body = {}
                    # 请求收到时间
                    start_time = DateTime.get_datetime_now_str()

                    log_data = cls.__make_log_data(client_type=client_type, ip_address=ip_address,
                                                   user_id=user_id, url=url, http_method=http_method,
                                                   header=header, params=params, body=body,
                                                   start_time=start_time)

                    # request中记录日志id
                    request.log_id = RequestLogModel(req=request).create(log_data)


                    result = func(args, kwargs)
                except Exception as e:
                    is_success = False
                    msg = "未知异常"
                    traceback_msg = traceback.print_exc()
                    raise e
                else:
                    is_success = True
                    msg = "成功"
                    traceback_msg = None
                finally:
                    # 请求返回值
                    return_data = result[0] if result else None

                    # 请求结束时间
                    end_time = DateTime.get_datetime_now_str()

                    update_log_data = cls.__make_update_log_data(end_time=end_time, is_success=is_success, msg=msg,
                                                                 traceback=traceback_msg, return_data=return_data)

                    RequestLogModel(request).update(request.log_id, update_log_data)
                    return result

            return wrapper

        return decorated
