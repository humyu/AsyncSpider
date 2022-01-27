# -*- coding: utf-8 -*-
"""
重试
"""


def retry_if_bad_code(result):
    # 返回 True，则重试
    return False if result == 200 else True


def retry_if_exception(exception):
    print(f"异常: {exception}")
    return isinstance(exception, Exception)
