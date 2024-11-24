# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/20
Last Modified: 2023/11/20
Description: 
"""
def make_response(code, msg, data=None):
    """
    响应数据构造函数

    :param code: int. 错误码
    :param msg: str. 错误信息
    :param data: dict or none. 其他信息，用于传递一些数据信息分析错误，一般为None。
    :return:
    """
    resp = {
        'code': code,
        'msg': msg
    }

    if data:
        resp.update({'data': data})

    return resp


class ResponseMaker:
    """
    自定义响应

    1: 成功
    1xxxx: 业务错误
    2xxxx: 系统错误
    """

    # 成功
    @staticmethod
    def success(data=None):
        """成功"""
        resp = make_response(200, "OK", data)
        return resp, 200

    # 1xxxx，业务返回值
    @staticmethod
    def not_exist(obj_name, condition):
        """对象不存在"""
        if not obj_name:
            raise Exception("obj_name不能为空")

        # err_msg = f"{obj_name}不存在，查询条件是{condition}"
        err_msg = f"{obj_name}不存在"
        return make_response(10001, err_msg), 200

    @staticmethod
    def user_password_error():
        return make_response(10002, "用户密码错误"), 200

    @staticmethod
    def upload_file_type_error():
        return make_response(10003, "上传文件失败，file_type错误"), 200

    @staticmethod
    def old_password_error():
        return make_response(10004, "旧密码错误"), 200

    @staticmethod
    def file_not_exist():
        return make_response(10004, "文件不存在"), 200

    @staticmethod
    def banner_not_exist():
        return make_response(10005, "banner不存在"), 200

    @staticmethod
    def user_account_exist():
        return make_response(10005, "账号已存在"), 200

    @staticmethod
    def image_not_exist():
        return make_response(10006, "图片不存在"), 200

    @staticmethod
    def document_status_error():
        return make_response(10007, "档案状态错误"), 200

    @staticmethod
    def document_import_error():
        return make_response(10008, "excel导入失败"), 200

    @staticmethod
    def import_document_id_error():
        return make_response(10009, "document_id错误"), 200

    @staticmethod
    def is_exist(obj_name):
        err_msg = f"{obj_name}已存在"
        return make_response(10010, err_msg), 200

    @staticmethod
    def document_has_data():
        return make_response(10011, "档案中还有育种数据，无法删除"), 200

    @staticmethod
    def login_enterprise_disable():
        return make_response(10012, "企业已停用"), 200

    @staticmethod
    def account_permission_deny():
        return make_response(10013, "账号权限不足，操作失败"), 200

    @staticmethod
    def document_import_status_deny():
        return make_response(10014, "档案导入状态不是未导入状态，无法导入"), 200

    @staticmethod
    def missing_params(param_name):
        return make_response(10015, f"{param_name}不可为空"), 200

    @staticmethod
    def new_password_same_to_old():
        return make_response(10016, f"新密码和旧密码相同"), 200

    @staticmethod
    def login_enterprise_deprecated():
        return make_response(10017, f"企业授权过期"), 200

    @staticmethod
    def login_enterprise_deleted():
        return make_response(10018, f"企业已被删除"), 200

    @staticmethod
    def land_is_used():
        return make_response(10019, f"土地正在使用中，无法删除"), 200

    @staticmethod
    def seed_name_exist():
        return make_response(10020, f"种子名称重复"), 200

    @staticmethod
    def seed_code_exist():
        return make_response(10021, f"种子编号重复"), 200

    @staticmethod
    def seed_has_reference(data):
        return make_response(10022, f"种子正在被使用", data=data), 200

    @staticmethod
    def stash_is_enable():
        return make_response(10023, f"仓库为启用状态，无法删除"), 200

    @staticmethod
    def document_column_name_duplicated(columns: str):
        return make_response(10024, f"档案列名重复, 重复列为：{columns}"), 200

    @staticmethod
    def document_locked():
        return make_response(10025, f"档案已锁定"), 200

    @staticmethod
    def breeding_list_name_duplicated():
        return make_response(10026, f"育种数据中种子名称重复"), 200

    @staticmethod
    def breeding_list_code_duplicated():
        return make_response(10026, f"育种数据中种子编号重复"), 200

    @staticmethod
    def document_seed_not_exist():
        return make_response(10027, f"档案内种子不存在"), 200

    @staticmethod
    def land_name_duplicated():
        """土地名称重复"""
        return make_response(10028, "土地名称重复"), 200

    @staticmethod
    def document_name_duplicated():
        """档案名称重复"""
        return make_response(10029, "档案名称重复"), 200

    @staticmethod
    def document_data_column_error(desc):
        """档案名称重复"""
        error_msg = "档案数据列名错误." + desc
        return make_response(10030, error_msg), 200

    @staticmethod
    def document_import_type_error():
        """档案名称重复"""
        return make_response(10031, "参数import_type枚举值错误。可选值为: APPEND, COVER"), 200

    @staticmethod
    def document_data_import_failed(msg):
        """档案导入失败"""
        return make_response(10032, f"档案数据导入失败。原因：{msg}"), 200

    # 2xxxx，系统返回值
    @staticmethod
    def token_missing():
        return make_response(20001, "请求头缺少token"), 401

    @staticmethod
    def token_expire():
        return make_response(20002, "token过期"), 401

    @staticmethod
    def token_error():
        return make_response(20003, "token错误"), 401

    @staticmethod
    def not_admin():
        return make_response(20005, "非管理员账号，无法操作"), 200

    @staticmethod
    def id_format_error():
        return make_response(20006, "id格式错误"), 200

    @staticmethod
    def enterprise_disable():
        return make_response(20008, "企业已停用"), 401

    @staticmethod
    def enterprise_authorization_deprecated():
        return make_response(20009, "企业授权过期"), 401

    @staticmethod
    def enterprise_deleted():
        return make_response(20010, "企业已被删除"), 401

    @staticmethod
    def can_not_delete_admin_user():
        return make_response(20011, "无法删除管理员，因为这是最后一个管理员账号"), 200

    @staticmethod
    def can_not_delete_root_user():
        return make_response(20012, "无法删除企业的根账号"), 200

    @staticmethod
    def request_param_error(msg):
        """
        请求参数错误

        :param msg: str. 错误描述
        :return:
        """
        return make_response(20013, msg), 200


