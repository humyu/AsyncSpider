# -*- coding: utf-8 -*-
import time
from concurrent.futures import ThreadPoolExecutor


def spider(page):
    time.sleep(page)
    return page


start = time.time()
executor = ThreadPoolExecutor(max_workers=4)

i = 1
for result in executor.map(spider, [2, 3, 1, 4]):
    print("task{}:{}".format(i, result))
    i += 1

