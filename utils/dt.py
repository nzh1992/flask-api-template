# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/26
Last Modified: 2023/12/26
Description: 
"""
import time
from datetime import datetime, timedelta


class DateTime:
    """
    获取时间（北京时间）
    """
    FORMAT = "%Y-%m-%d %H:%M:%S"

    @classmethod
    def get_timezone(cls):
        timezone = time.tzname[time.localtime().tm_isdst]
        return timezone

    @classmethod
    def get_datetime_now(cls):
        if cls.get_timezone() == "UTC":
            # 如果时UTC时区，转为北京时间
            bj_now = datetime.now() + timedelta(hours=8)
            return bj_now
        else:
            return datetime.now()

    @classmethod
    def get_datetime_now_str(cls, custom_format=None):
        if not custom_format:
            format = cls.FORMAT
        else:
            format = custom_format

        if cls.get_timezone() == "UTC":
            # 如果时UTC时区，转为北京时间
            bj_now = datetime.now() + timedelta(hours=8)
            return bj_now.strftime(format)
        else:
            return datetime.now().strftime(format)
