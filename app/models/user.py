# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/8
Last Modified: 2023/12/8
Description: 用户模块
"""
from .basic import BasicModel


class User(BasicModel):
    """
    intellifield数据库，user表
    """
    def __init__(self, req=None, db=None):
        if db is not None:
            super(User, self).__init__(db=db)
        else:
            super(User, self).__init__(req=req)

    def get_count(self, enterprise_id):
        """
        所有用户都在同一张表中，所以需要先拿到企业id

        :param enterprise_id: str. 企业id
        :return:
        """
        condition = {"enterprise_id": enterprise_id}
        count = self.db.user.count_documents(condition)
        return count

