# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/12/6
Last Modified: 2023/12/6
Description: 二维码
"""
import os

import qrcode
from bson import ObjectId

from .basic import BasicModel


class QRCode(BasicModel):
    def __init__(self, data, req=None, db=None):
        if db is not None:
            super(QRCode, self).__init__(db=db)
        else:
            super(QRCode, self).__init__(req=req)

        self.collection_name = "image"

        self.data = data
        self.version = 2
        self.box_size = 6
        self.border = 2
        self.qr_code = qrcode.QRCode(
            version=self.version,
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=self.box_size,
            border=self.border
        )

    def save(self):
        """
        将生成好的二维码图片，保存到mongodb，返回图片url
        """
        file_name = "QR.png"
        img_fp = os.path.join(os.getcwd(), "data", file_name)

        self.qr_code.clear()
        self.qr_code.add_data(self.data)
        self.qr_code.make(fit=True)

        # 保存图片到服务器本地
        img = self.qr_code.make_image()
        img.save(img_fp)

        # 读取并写入mongo
        with open(img_fp, 'rb') as f:
            img_bytes = f.read()

        img_data = {
            "name": file_name,
            "data": img_bytes
        }
        result = self.db[self.collection_name].insert_one(img_data)

        return str(result.inserted_id)
