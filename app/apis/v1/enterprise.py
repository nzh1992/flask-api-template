# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/28
Last Modified: 2023/11/28
Description: 
"""
from flask import request, current_app
from flask_restx import Resource, Namespace, fields
from bson import ObjectId

from utils.response import ResponseMaker
# from utils.mongo import Mongo
from app.extentions import mongo
from utils.jwt import JWTUtil
from app.models.enterprise import Enterprise
from utils.log import RequestLogUtil


enterprise_api = Namespace("client", description="客户端API", path="/client_api/v1/enterprise")

enterprise_model = enterprise_api.model('EnterpriseModel', {
    'logo': fields.String(required=False, description='企业logo'),
    'hotline': fields.String(required=False, description='企业热线'),
    'email': fields.String(required=False, description='企业邮箱')
})


@enterprise_api.route('/')
class EnterpriseAPI(Resource):
    @enterprise_api.doc(description='获取企业信息')
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
