# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/11
Last Modified: 2023/12/11
Description: 消息通知
"""
from flask import request
from flask_restx import Resource, Namespace, fields

from utils.response import ResponseMaker
from utils.jwt import JWTUtil
from utils.log import RequestLogUtil
from app.models.notify import Notify


notify_api = Namespace("client", description="客户端API", path="/api/v1/notify")


@notify_api.route('/list')
class NotifyAPI(Resource):
    @notify_api.doc(description='通知消息列表')
    @JWTUtil.verify_token_decorator(request)
    def post(self, *args, **kwargs):
        data = request.get_json(force=True)
        pn = data.get("pn")
        pz = data.get("pz")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        status = data.get("status")
        keyword = data.get("keyword")

        result = Notify(req=request).query_list(pn, pz, start_date, end_date, status, keyword)

        notify_list = []

        for notify in result.get("list"):
            notify_data = {
                "id": str(notify.get("_id")),
                "title": notify.get("title"),
                "date": notify.get("date"),
                "status": notify.get("status")
            }
            notify_list.append(notify_data)

        resp_data = {
            'total': result.get('total'),
            "list": notify_list
        }
        return resp_data


@notify_api.route('/<id>')
class NotifyDetailAPI(Resource):
    @notify_api.doc(description='通知消息详情')
    @JWTUtil.verify_token_decorator(request)
    def get(self, *args, **kwargs):
        notify_id = request.view_args.get("id")
        notify_data = Notify(req=request).get(notify_id)
        return ResponseMaker.success(notify_data)


@notify_api.route('/unread_count')
class NotifyUnreadCountAPI(Resource):
    @notify_api.doc(description='获取未读消息数量')
    @JWTUtil.verify_token_decorator(request)
    def get(self, *args, **kwargs):
        count = Notify(req=request).get_unread_count()
        resp_data = {'quantity': count}

        return ResponseMaker.success(resp_data)


@notify_api.route('/read')
class NotifyUnreadCountAPI(Resource):
    @notify_api.doc(description='阅读消息')
    @JWTUtil.verify_token_decorator(request)
    @RequestLogUtil.log(request)
    def post(self, *args, **kwargs):
        data = request.get_json(force=True)
        ids = data.get("ids")
        Notify(req=request).read(ids)

        return ResponseMaker.success()