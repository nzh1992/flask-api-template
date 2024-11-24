# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2024/11/24
Last Modified: 2024/11/24
Description: 
"""
from flask_restx import Api

from .auth import auth_api


api = Api(
    title="API",
    version="1.0",
    description="API目录",
    security="Bearer Auth",
    authorizations={
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "在请求头中使用Authorization字段传递token"
        }
    }
)


api.add_namespace(auth_api)