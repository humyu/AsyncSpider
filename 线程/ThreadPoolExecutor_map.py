# -*- coding: utf-8 -*-
import time
from concurrent.futures import ThreadPoolExecutor

"""
map(fn, *iterables, timeout=None)
fn： 第一个参数 fn 是需要线程执行的函数；
iterables：第二个参数接受一个可迭代对象；
timeout： 第三个参数 timeout 跟 wait() 的 timeout 一样，
但由于 map 是返回线程执行的结果，如果 timeout小于线程执行时间会抛异常 TimeoutError。
"""


def spider(page):
    time.sleep(page)
    return page


start = time.time()
executor = ThreadPoolExecutor(max_workers=4)

i = 1
for result in executor.map(spider, [2, 3, 1, 4]):
    print("task{}:{}".format(i, result))
    i += 1
