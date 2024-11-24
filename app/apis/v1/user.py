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
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

from app.extentions import mongo
from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from utils.log import RequestLogUtil


user_api = Namespace("client", description="客户端API", path="/client_api/v1/user")

user_model = user_api.model('UserModel', {
    'phone_number': fields.String(required=True, description='手机号'),
    'password': fields.String(required=True, description='密码'),
    'user_name': fields.String(required=True, description='用户姓名'),
    'role': fields.String(required=True, description='账号角色')
})

user_list_model = user_api.model('UserListModel', {
    'page_number': fields.String(required=True, description='页码'),
    'page_size': fields.String(required=True, description='每页数量'),
    'role': fields.String(required=False, description='角色'),
    'keyword': fields.String(required=False, description='成员姓名/手机号码')
})

change_password_model = user_api.model('ChangePasswordModel', {
    'old_password': fields.String(required=True, description='旧密码'),
    'new_password': fields.String(required=True, description='新密码'),
})


@user_api.route('/')
class UserAPI(Resource):
    @user_api.doc(description='添加用户', body=user_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def put(self, *args, **kwargs):
        data = json.loads(request.data)
        phone_number = data.get("phone_number")
        password = data.get("password")
        user_name = data.get("user_name")
        role = data.get("role")

        # 判断账号是否重复
        user = mongo.db.user.find_one({"phone_number": phone_number})
        if user:
            return ResponseMaker.user_account_exist()

        user_data = {
            "phone_number": phone_number,
            "password": password,
            "user_name": user_name,
            "role": role,
            "enterprise_id": request.user.get("enterprise_id"),
            "is_root": False
        }

        mongo.db.user.insert_one(user_data)

        return ResponseMaker.success()


@user_api.route('/<id>')
class ChangeUserAPI(Resource):
    @user_api.doc(description='删除用户', params={'id': '用户id'}, body=user_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def delete(self, params, *args, **kwargs):
        if request.user.get("role") != "ADMIN":
            return ResponseMaker.account_permission_deny()

        try:
            condition = {'_id': ObjectId(request.view_args.get("id"))}
        except Exception:
            return ResponseMaker.id_format_error()

        user = mongo.db.user.find_one(condition)
        if not user:
            return ResponseMaker.not_exist("用户", {"id": request.view_args.get("id")})

        # 如果是企业的根用户，不可删除
        if user.get("is_root"):
            return ResponseMaker.can_not_delete_root_user()

        mongo.db.user.delete_one(condition)
        return ResponseMaker.success()

    @user_api.doc(description='查看用户', params={'id': '用户id'})
    @JWTUtil.verify_token_decorator(request)
    def get(self, params, *args, **kwargs):
        try:
            condition = {'_id': ObjectId(request.view_args.get("id"))}
        except Exception:
            return ResponseMaker.id_format_error()

        user = mongo.db.user.find_one(condition)
        if not user:
            return ResponseMaker.not_exist("用户", {"id": request.view_args.get("id")})

        user_data = {
            "id": str(user.get("_id")),
            "phone_number": user.get("phone_number"),
            "user_name": user.get("user_name"),
            "role": user.get("role"),
            "is_root": user.get("is_root"),
            "password": user.get("password")
        }

        return ResponseMaker.success(user_data)

    @user_api.doc(description='修改用户', params={'id': '用户id'}, body=user_model)
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def patch(self, params, *args, **kwargs):
        try:
            obj_id = ObjectId(request.view_args.get("id"))
            user = mongo.db.user.find_one({"_id": obj_id})
        except Exception:
            return ResponseMaker.not_exist("用户", {"id": request.view_args.get("id")})

        data = json.loads(request.data)
        phone_number = data.get("phone_number")
        password = data.get("password")
        user_name = data.get("user_name")
        role = data.get("role")

        user_data = {
            "$set": {
                "phone_number": phone_number,
                "password": password,
                "user_name": user_name,
                "role": role
            }
        }

        # 判断账号是否重复
        count = mongo.db.user.count_documents({"phone_number": phone_number})
        if count > 1:
            return ResponseMaker.user_account_exist()

        mongo.db.user.update_one({'_id': obj_id}, user_data)

        # 企业root账号，同步更新账号信息到企业表
        if user.get("is_root"):
            enterprise_id = user.get("enterprise_id")
            update_data = {
                "$set": {
                    "phone_number": phone_number,
                    "password": password,
                    "user_name": user_name
                }
            }
            mongo.db.enterprise.update_one({"_id": ObjectId(enterprise_id)}, update_data)

        return ResponseMaker.success()


@user_api.route('/list')
class UserListAPI(Resource):
    @user_api.doc(description='用户列表', body=user_list_model)
    @JWTUtil.verify_token_decorator(request)
    def post(self, *args, **kwargs):
        data = json.loads(request.data)
        role = data.get("role")
        keyword = data.get("keyword")   # 姓名、手机号码、账号
        page_number = data.get('page_number')
        page_size = data.get('page_size')

        condition = {}

        # 仅查看当前企业的用户
        condition.update({"enterprise_id": request.user.get("enterprise_id")})

        # 关键字条件
        if keyword:
            condition.update({
                "$or": [
                    {'user_name': {'$regex': keyword}},
                    {'phone_number': {'$regex': keyword}}
                ]
            })

        # 角色条件
        if role:
            condition.update({'role': role})

        # 用户总数
        total = mongo.db.user.count_documents(condition)

        # 分页查询
        start = (page_number - 1) * page_size
        user_list = mongo.db.user.find(condition).skip(start).limit(page_size)

        user_data_list = []
        for user in user_list:
            user_data = {
                "id": str(user.get("_id")),
                "phone_number": user.get("phone_number"),
                "user_name": user.get("user_name"),
                "role": user.get("role"),
                "is_root": user.get("is_root")
            }
            user_data_list.append(user_data)

        resp_data = {
            'total': total,
            'list': user_data_list
        }

        return ResponseMaker.success(resp_data)
