# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/7/19
Last Modified: 2023/7/19
Description: 
"""
from flask_restx import Api


# from .healthy import healthy_api
from .v1.user import user_api
from .v1.auth import auth_api
from .v1.upload import upload_api
from .v1.region import region_api
from .v1.land import land_api
from .v1.document import document_api
from .v1.enterprise import enterprise_api
from .v1.image import image_api
from .v1.banner import banner_api
from .v1.workbench import workbench_api
from .v1.stash import stash_api
from .v1.seed import seed_api
from .v1.download import download_api
from .v1.device import device_api
from .v1.video import video_api
from .v1.notify import notify_api
from .v1.default_enter import default_enter_api
from .v1.document_data import document_data_api
from .wx_v1.auth import wx_auth_api
from .wx_v1.workbench import wx_workbench_api
from .wx_v1.enterprise import wx_enterprise_api
from .wx_v1.user import wx_user_api
from .wx_v1.land import wx_land_api
from .wx_v1.notify import wx_notify_api
from .wx_v1.document import wx_document_api
from .wx_v1.region import wx_region_api
from .wx_v1.stash import wx_stash_api
from .wx_v1.seed import wx_seed_api
from .wx_v1.upload import wx_upload_api
from .wx_v1.image import wx_image_api
from .wx_v1.video import wx_video_api
from .wx_v1.device import wx_device_api
from .wx_v1.document_data import wx_document_data_api
from .wx_v1.default_enter import wx_default_enter_api
from .admin_v1.auth import admin_auth_api
from .admin_v1.admin_user import admin_user_api
from .admin_v1.enterprise import admin_enterprise_api
from .admin_v1.workbench import admin_workbench_api


api = Api(
    title="农智云API",
    version="2.0",
    description="农智云API（开发中...）",
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


# web端 API
api.add_namespace(user_api)
api.add_namespace(auth_api)
api.add_namespace(upload_api)
api.add_namespace(region_api)
api.add_namespace(land_api)
api.add_namespace(document_api)
api.add_namespace(enterprise_api)
# api.add_namespace(image_api)
# api.add_namespace(workbench_api)
# api.add_namespace(stash_api)
# api.add_namespace(seed_api)
# api.add_namespace(download_api)
# api.add_namespace(banner_api)
# api.add_namespace(device_api)
# api.add_namespace(video_api)
# api.add_namespace(notify_api)
api.add_namespace(default_enter_api)
api.add_namespace(document_data_api)

# 小程序 API
api.add_namespace(wx_auth_api)
# api.add_namespace(wx_workbench_api)
api.add_namespace(wx_enterprise_api)
api.add_namespace(wx_user_api)
# api.add_namespace(wx_land_api)
# api.add_namespace(wx_notify_api)
api.add_namespace(wx_document_api)
# api.add_namespace(wx_stash_api)
# api.add_namespace(wx_seed_api)
# api.add_namespace(wx_region_api)
api.add_namespace(wx_upload_api)
# api.add_namespace(wx_image_api)
# api.add_namespace(wx_video_api)
# api.add_namespace(wx_device_api)
api.add_namespace(wx_document_data_api)
api.add_namespace(wx_default_enter_api)

# 后台管理 API
api.add_namespace(admin_auth_api)
api.add_namespace(admin_user_api)
api.add_namespace(admin_enterprise_api)
api.add_namespace(admin_workbench_api)