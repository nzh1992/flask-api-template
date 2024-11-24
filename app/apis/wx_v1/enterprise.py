# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/16
Last Modified: 2023/12/16
Description: 
"""
from bson import ObjectId
from flask import request
from flask_restx import Resource, Namespace, fields

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from app.extentions import mongo


wx_enterprise_api = Namespace("app", description="移动端API", path="/app_api/v1/enterprise")


wx_enterprise_model = wx_enterprise_api.model('EnterpriseModel', {
    'name': fields.String(required=False, description='企业名称'),
    'logo': fields.String(required=False, description='企业logo'),
    'hotline': fields.String(required=False, description='企业热线'),
    'email': fields.String(required=False, description='企业邮箱')
})


@wx_enterprise_api.route('/')
class EnterpriseAPI(Resource):
    @wx_enterprise_api.doc(description='获取企业信息')
    @JWTUtil.verify_token_decorator(request)
    def get(self, params, *args, **kwargs):
        # 获取用户所在企业id
        enterprise_id = request.user.get("enterprise_id")

        enterprise = mongo.db.enterprise.find_one({"_id": ObjectId(enterprise_id)})
        if not enterprise:
            return ResponseMaker.not_exist(f"企业id: {enterprise_id}", {})

        company_data = {
            "id": str(enterprise.get("_id")),
            "name": enterprise.get("name"),
            "start_date": enterprise.get("start_date"),
            "end_date": enterprise.get("end_date"),
        }

        return ResponseMaker.success(company_data)
