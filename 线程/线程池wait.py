# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED
import time


def spider(page):
    time.sleep(page)
    print(f"crawl task{page} finished")
    return page


with ThreadPoolExecutor(max_workers=5) as t:
    all_task = [t.submit(spider, page) for page in range(1, 5)]
    # fs: 表示需要执行的序列
    # return_when：表示wait返回结果的条件，默认为 ALL_COMPLETED 全部执行完成再返回
    # FIRST_COMPLETED：当完成第一个任务的时候，就停止等待，继续主线程任务
    wait(fs=all_task, return_when=FIRST_COMPLETED)
    print('finished')
    print(wait(all_task, timeout=2.5))
