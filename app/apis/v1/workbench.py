# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/30
Last Modified: 2023/11/30
Description: 工作台
"""
from flask import request
from flask_restx import Resource, Namespace

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from app.models.seed import Seed
from app.models.land import Land
from app.models.user import User


workbench_api = Namespace("client", description="客户端API", path="/api/v1/workbench")


@workbench_api.route('/')
class WorkbenchAPI(Resource):
    @workbench_api.doc(description='获取工作台数据')
    @JWTUtil.verify_token_decorator(request)
    def get(self, *args, **kwargs):
        # 1.种子数量
        seed_count = Seed(req=request).get_count()

        # 2.土地数量
        land_count = Land(req=request).get_count()

        # 3.设备数量
        facility_count = 0

        # 4.用户数量
        enterprise_id = request.user.get("enterprise_id")
        user_count = User(req=request).get_count(enterprise_id)

        # 数量汇总
        quantity_statistic = {
            'seed': seed_count,
            'land': land_count,
            'facility': facility_count,
            'user': user_count
        }

        # 土地汇总
        land_data_list = Land(req=request).get_all_of_location()

        resp_data = {
            "quantity_statistic": quantity_statistic,
            "land_list": land_data_list
        }

        return ResponseMaker.success(resp_data)

