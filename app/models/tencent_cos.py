# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2024/9/4
Last Modified: 2024/9/4
Description: 腾讯云，对象存储(COS)
"""
from qcloud_cos import CosConfig, CosS3Client, CosServiceError, CosClientError


class TencentCos:
    """腾讯云，对象存储服务"""
    def __init__(self):
        self.app_id = "1319070333"
        self.secret_id = "AKIDxlOn2Z3hvCQcntnUSGya3f6MOJ1Yx973"
        self.secret_key = "Hk8JZikdIG8mBNT7nXEh072kFXcJyUnw"
        self.region = 'ap-shanghai'

        # 数据桶
        self.bucket_image = "image-1319070333"
        self.bucket_excel = "excel-1319070333"

        self.config = CosConfig(Region=self.region, SecretId=self.secret_id,
                                SecretKey=self.secret_key, Token=None, Domain=None)
        self.client = CosS3Client(self.config)

    def __upload(self, bucket, file_stream, file_name):
        """
        上传，封装了qcloud_cos上传功能

        :param bucket: str. 上传到哪个数据桶
        :param file_stream: bytes. 文件的字节流
        """
        if "image" in bucket:
            response = self.client.put_object(
                Bucket=bucket,
                Body=file_stream,
                Key=file_name,
                ContentDisposition='inline'
            )
            # 获取url
            url = self.client.get_object_url(Bucket=self.bucket_image, Key=file_name)
        elif "excel" in bucket:
            response = self.client.put_object(
                Bucket=bucket,
                Body=file_stream,
                Key=file_name
            )
            # 获取url
            url = self.client.get_object_url(Bucket=self.bucket_excel, Key=file_name)

        return url

    def upload_image(self, image_file, file_name):
        """
        上传图片
        """
        url = self.__upload(self.bucket_image, image_file, file_name)
        return url

    def upload_excel(self, excel_file, file_name):
        """
        上传excel
        """
        url = self.__upload(self.bucket_excel, excel_file, file_name)
        return url