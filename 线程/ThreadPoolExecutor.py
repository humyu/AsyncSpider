# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
import time


def spider(page):
    time.sleep(page)
    print(f"crawl task{page} finished")
    return page


# max_workers：设置线程池中最多能同时运行的线程数目
with ThreadPoolExecutor(max_workers=5) as t:
    # 通过submit函数来提交线程需要执行的函数到线程池中，并返回句柄
    # submit() 不是阻塞的，而是立即返回
    task1 = t.submit(spider, 1)
    print("执行task1")
    task2 = t.submit(spider, 2)
    print("执行task2")
    task3 = t.submit(spider, 3)
    print("执行task3")

    # 通过done来判断线程是否完成
    print(f"task1: {task1.done()}")
    print(f"task2: {task2.done()}")
    print(f"task3: {task3.done()}")

    time.sleep(2.5)
    print(f"task1: {task1.done()}")
    print(f"task2: {task2.done()}")
    print(f"task3: {task3.done()}")
    # 通过result来获取返回值
    print(f"result:{task1.result()}")
    print(f"result:{task2.result()}")
    print(f"result:{task3.result()}")
