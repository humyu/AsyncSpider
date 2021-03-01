# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


def spider(page):
    time.sleep(page)
    print(f"crawl task{page} finished")
    return page


def main():
    """
    as_completed() 方法是一个生成器，在没有任务完成的时候，会一直阻塞，除非设置了 timeout。
    当有某个任务完成的时候，会 yield 这个任务，就能执行 for 循环下面的语句，然后继续阻塞住，循环到所有的任务结束。
    同时，先完成的任务会先返回给主线程。
    :return:
    """
    with ThreadPoolExecutor(max_workers=5) as t:
        obj_list = []
        for page in range(1, 5):
            obj = t.submit(spider, page)
            obj_list.append(obj)

        for future in as_completed(obj_list):
            data = future.result()
            print(f"main: {data}")
