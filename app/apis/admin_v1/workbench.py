# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/10
Last Modified: 2023/12/10
Description: 
"""
from flask import request
from flask_restx import Resource, Namespace

from utils.response import ResponseMaker
from utils.jwt import JWTUtil


admin_workbench_api = Namespace("admin", description="管理端API", path="/admin_api/v1/workbench")


@admin_workbench_api.route('/')
class AdminWorkbenchAPI(Resource):
    @admin_workbench_api.doc(description='获取工作台数据')
    @JWTUtil.verify_token_decorator(request)
    def get(self, *args, **kwargs):
        resp_data = []
        return ResponseMaker.success(resp_data)
