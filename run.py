# -*- coding: utf-8 -*-
"""
Author: niziheng
Created Date: 2023/11/7
Last Modified: 2023/11/7
Description: 
"""
import app as app_package


app = app_package.create_app()


if __name__ == '__main__':
    app.run()
