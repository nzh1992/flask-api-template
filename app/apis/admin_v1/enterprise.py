# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/7
Last Modified: 2023/12/7
Description: 
"""
import json

from flask import request, current_app
from flask_restx import Resource, Namespace, fields
from bson import ObjectId
from werkzeug.security import generate_password_hash

from app.extentions import mongo
from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from utils.mongo import Mongo
from app.models.banner import Banner
from utils.log import RequestLogUtil


admin_enterprise_api = Namespace("admin", description="管理端API", path="/admin_api/v1/enterprise")

admin_enterprise_model = admin_enterprise_api.model('AdminEnterpriseModel', {
    'name': fields.String(required=True, description='企业名称'),
    'phone_number': fields.String(required=True, description='手机号码'),
    'password': fields.String(required=True, description='企业账号密码'),
    'start_date': fields.String(required=False, description='授权开始时间'),
    'end_date': fields.String(required=False, description='授权结束时间'),
    'user_name': fields.String(required=False, description='用户姓名'),
})

admin_enterprise_status_model = admin_enterprise_api.model("AdminEnterpriseStatusModel", {
    'id': fields.String(required=True, description='企业id'),
    'status': fields.String(required=True, description='状态，停用/启用'),
})


admin_enterprise_list_model = admin_enterprise_api.model("AdminEnterpriseListModel", {
    'page_number': fields.Integer(required=True, description='第几页', default=1),
    'page_size': fields.Integer(required=True, description='每页数量', default=10),
    'keyword': fields.String(required=False, description='关键字'),
    'start_date': fields.String(required=False, description='有效开始时间'),
    'end_date': fields.String(required=False, description='有效结束时间'),
    'status': fields.String(required=False, description='状态')
})


@admin_enterprise_api.route('/')
class AdminEnterpriseAPI(Resource):
    @admin_enterprise_api.doc(description='添加公司', body=admin_enterprise_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def put(self, *args, **kwargs):
        data = request.get_json(force=True)
        name = data.get("name")                  # 企业名称
        phone_number = data.get("phone_number")  # 手机号作为账号
        password = data.get("password")          # 密码
        start_date = data.get("start_date")      # 授权周期-开始日期
        end_date = data.get("end_date")          # 授权周期-结束日期
        user_name = data.get("user_name")        # 用户姓名

        # 默认状态，启用
        status = "ENABLE"

        # 判断企业名称是否重复
        enterprise = mongo.db.enterprise.find_one({"name": name})
        if enterprise:
            return ResponseMaker.is_exist("企业名称")

        # 判断企业账号是否重复
        enterprise = mongo.db.user.find_one({"phone_number": phone_number})
        if enterprise:
            return ResponseMaker.is_exist("企业账号（手机号）")

        company_data = {
            "name": name,
            "phone_number": phone_number,
            "password": password,
            "start_date": start_date,
            "end_date": end_date,
            "user_name": user_name,
            "status": status
        }

        result = mongo.db.enterprise.insert_one(company_data)
        enterprise_id = str(result.inserted_id)

        # 更新企业数据库名称
        # 名称格式： "NZY_{enterprise_id}"
        db_name = f"NZY_{enterprise_id}"
        mongo.db.enterprise.update_one({"_id": ObjectId(enterprise_id)}, {"$set": {"db_name": db_name}})

        # 1. 创建企业时，同时为此企业创建默认管理员账号
        admin_user_data = {
            "phone_number": phone_number,
            "password": password,
            "user_name": user_name,
            "role": "ADMIN",
            "enterprise_id": str(result.inserted_id),
            "is_root": True
        }
        mongo.db.user.insert_one(admin_user_data)

        return ResponseMaker.success()


@admin_enterprise_api.route('/<id>')
class ChangeEnterpriseAPI(Resource):
    @admin_enterprise_api.doc(description='查看企业信息', params={'id': '企业id'})
    @JWTUtil.verify_token_decorator(request)
    def get(self, params, *args, **kwargs):
        try:
            condition = {'_id': ObjectId(request.view_args.get("id"))}
            enterprise = mongo.db.enterprise.find_one(condition)
            if not enterprise:
                return ResponseMaker.not_exist("企业", {})
        except Exception:
            return ResponseMaker.not_exist("企业", {})

        enterprise_data = {
            "id": str(enterprise.get("_id")),
            "name": enterprise.get("name"),
            "phone_number": enterprise.get("phone_number"),
            "password": enterprise.get("password"),
            "start_date": enterprise.get("start_date"),
            "end_date": enterprise.get("end_date"),
            "user_name": enterprise.get("user_name"),
            "status": enterprise.get("status")
        }

        return ResponseMaker.success(enterprise_data)

    @admin_enterprise_api.doc(description='修改企业信息', params={'id': '企业id'}, body=admin_enterprise_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def patch(self, params, *args, **kwargs):
        try:
            obj_id = ObjectId(request.view_args.get("id"))
            condition = {'_id': obj_id}
            enterprise = mongo.db.enterprise.find_one(condition)
            if not enterprise:
                return ResponseMaker.not_exist("企业", {})
        except Exception:
            return ResponseMaker.not_exist("企业", {})

        data = json.loads(request.data)
        name = data.get("name")
        phone_number = data.get("phone_number")
        password = data.get("password")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        user_name = data.get("user_name")

        company_data = {
            "$set": {
                "name": name,
                "phone_number": phone_number,
                "password": password,
                "start_date": start_date,
                "end_date": end_date,
                "user_name": user_name
            }
        }

        # 判断企业名称是否重复
        count = mongo.db.enterprise.count_documents({"name": name})
        if count > 1:
            return ResponseMaker.is_exist("企业名称")

        # 判断企业账号是否重复
        count = mongo.db.user.count_documents({"phone_number": phone_number})
        if count > 1:
            return ResponseMaker.is_exist("企业账号")

        mongo.db.enterprise.update_one({'_id': obj_id}, company_data)

        # 同步更新用户表中企业账号信息
        user_condition = {"enterprise_id": str(obj_id), "is_root": True}
        user_info = {
            "$set": {
                "phone_number": phone_number,
                "password": password,
                "user_name": user_name,
            }
        }
        mongo.db.user.update_one(user_condition, user_info)

        return ResponseMaker.success()


@admin_enterprise_api.route('/list')
class AdminEnterpriseListAPI(Resource):
    @admin_enterprise_api.doc(description='企业列表', body=admin_enterprise_list_model)
    @JWTUtil.verify_token_decorator(request)
    def post(self, *args, **kwargs):
        data = request.get_json(force=True)
        page_number = data.get("page_number", 1)
        page_size = data.get("page_size", 10)
        keyword = data.get("keyword")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        status = data.get("status")

        condition = {}
        if keyword:
            # 关键字，模糊查询手机号和企业名称
            condition.update({
                "$or": [
                    {"phone_number": {"$regex": keyword}},
                    {"name": {"$regex": keyword}}
                ]
            })

        if start_date:
            condition.update({"start_date": {"$gte": start_date}})

        if end_date:
            condition.update({"end_date": {"$lte": end_date}})

        if status:
            condition.update({"status": status})

        start = (page_number - 1) * page_size
        enterprises = mongo.db.enterprise.find(condition).skip(start).limit(page_size)

        enterprise_count = mongo.db.enterprise.count_documents(condition)

        enterprise_data_list = []
        for enterprise in enterprises:
            enterprise_data = {
                "id": str(enterprise.get("_id")),
                "name": enterprise.get("name"),
                "phone_number": enterprise.get("phone_number"),
                "start_date": enterprise.get("start_date"),
                "end_date": enterprise.get("end_date"),
                "status": enterprise.get("status"),
                "user_name": enterprise.get("user_name")
            }
            enterprise_data_list.append(enterprise_data)

        resp_data = {
            "total": enterprise_count,
            "list": enterprise_data_list
        }

        return ResponseMaker.success(resp_data)


@admin_enterprise_api.route('/status')
class AdminEnterpriseStatusAPI(Resource):
    @admin_enterprise_api.doc(description='修改企业状态', body=admin_enterprise_status_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def post(self, *args, **kwargs):
        data = request.get_json(force=True)
        enterprise_id = data.get("id")
        status = data.get("status")

        update_data = {
            "$set": {
                "status": status
            }
        }
        mongo.db.enterprise.update_one({"_id": ObjectId(enterprise_id)}, update_data)
        return ResponseMaker.success()
