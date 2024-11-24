# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/7
Last Modified: 2023/11/7
Description: 
"""
import json

from flask import request
from flask_restx import Resource, Namespace, fields
from werkzeug.security import generate_password_hash
from bson import ObjectId

from app.extentions import mongo
from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from utils.log import RequestLogUtil


admin_user_api = Namespace("admin", description="管理端API", path="/admin_api/v1/admin_user")

admin_user_model = admin_user_api.model('AdminUserModel', {
    'phone_number': fields.String(required=True, description='手机号码'),
    'password': fields.String(required=True, description='密码'),
    'user_name': fields.String(required=True, description='姓名')
})

admin_user_list_model = admin_user_api.model('AdminUserListModel', {
    'page_number': fields.Integer(required=True, description='第几页', default=1),
    'page_size': fields.Integer(required=True, description='每页数量', default=10),
    'keyword': fields.String(required=False, description='关键字')
})

modify_admin_user_model = admin_user_api.model('ModifyAdminUserModel', {
    'phone_number': fields.String(required=False, description='手机号'),
    'password': fields.String(required=False, description='密码'),
    'user_name': fields.String(required=False, description='姓名')
})


@admin_user_api.route('/')
class AdminUserAPI(Resource):
    @admin_user_api.doc(description='添加管理员', body=admin_user_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def put(self, *args, **kwargs):
        data = json.loads(request.data)
        phone_number = data.get("phone_number")
        password = data.get("password")
        user_name = data.get("user_name")

        # 判断账号是否重复
        user = mongo.db.admin_user.find_one({"phone_number": phone_number})
        if user:
            return ResponseMaker.user_account_exist()

        user_data = {
            "phone_number": phone_number,
            "password": password,
            "user_name": user_name
        }

        mongo.db.admin_user.insert_one(user_data)

        return ResponseMaker.success()


@admin_user_api.route('/<id>')
class ChangeAdminUserAPI(Resource):
    @admin_user_api.doc(description='删除管理员', params={'id': '用户id'})
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def delete(self, params, *args, **kwargs):
        try:
            condition = {'_id': ObjectId(request.view_args.get("id"))}
        except Exception:
            return ResponseMaker.id_format_error()

        user = mongo.db.admin_user.find_one(condition)
        if not user:
            return ResponseMaker.not_exist("管理员", {})

        # 如果只剩一个管理员，无法删除
        admin_user_count = mongo.db.admin_user.count_documents({})
        if admin_user_count <= 1:
            return ResponseMaker.can_not_delete_admin_user()

        mongo.db.admin_user.delete_one(condition)
        return ResponseMaker.success()

    @admin_user_api.doc(description='查看管理员', params={'id': '用户id'})
    @JWTUtil.verify_token_decorator(request)
    def get(self, params, *args, **kwargs):
        try:
            condition = {'_id': ObjectId(request.view_args.get("id"))}
        except Exception:
            return ResponseMaker.id_format_error()

        user = mongo.db.admin_user.find_one(condition)
        if not user:
            return ResponseMaker.not_exist("管理员", {})

        user_data = {
            "id": str(user.get("_id")),
            "phone_number": user.get("phone_number"),
            "user_name": user.get("user_name"),
            "password": user.get("password")
        }

        return ResponseMaker.success(user_data)

    @admin_user_api.doc(description='修改管理员', params={'id': '用户id'}, body=modify_admin_user_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def patch(self, params, *args, **kwargs):
        try:
            obj_id = ObjectId(request.view_args.get("id"))
        except Exception:
            return ResponseMaker.id_format_error()

        data = json.loads(request.data)
        phone_number = data.get("phone_number")
        password = data.get("password")
        user_name = data.get("user_name")

        # 如果都是无效参数，则报错
        if not phone_number and not password and not user_name:
            error_msg = "phone_number, password, user_name都是无效值"
            return ResponseMaker.request_param_error(error_msg)

        user_data = {
            "$set": {}
        }

        # 如果传了手机号，连同手机号一起修改
        if phone_number:
            user_data["$set"]["phone_number"] = phone_number

        # 如果修改时不传密码，则不更新密码
        if password:
            user_data["$set"]["password"] = password

        # 如果传了姓名，连同姓名一起修改
        if user_name:
            user_data["$set"]["user_name"] = user_name

        # 判断账号是否重复
        user = mongo.db.admin_user.find_one({"phone_number": phone_number, "_id": {"$ne": obj_id}})
        if user:
            return ResponseMaker.user_account_exist()

        mongo.db.admin_user.update_one({'_id': obj_id}, user_data)
        return ResponseMaker.success()


@admin_user_api.route('/list')
class AdminUserListAPI(Resource):
    @admin_user_api.doc(body=admin_user_list_model, description='管理员列表')
    @JWTUtil.verify_token_decorator(request)
    def post(self, *args, **kwargs):
        data = request.get_json(force=True)
        page_number = data.get("page_number", 1)
        page_size = data.get("page_size", 10)
        keyword = data.get("keyword")

        condition = {}
        if keyword:
            condition.update({
                "$or":[
                    {"phone_number": {"$regex": keyword}},
                    {"user_name": {"$regex": keyword}}
                ]
            })

        start = (page_number - 1) * page_size

        admin_users = mongo.db.admin_user.find(condition).skip(start).limit(page_size)
        total = mongo.db.admin_user.count_documents(condition)

        admin_list = []
        for user in admin_users:
            user_data = {
                "id": str(user.get("_id")),
                "phone_number": user.get("phone_number"),
                "user_name": user.get("user_name")
            }
            admin_list.append(user_data)

        resp_data = {
            "total": total,
            "list": admin_list
        }

        return ResponseMaker.success(resp_data)
