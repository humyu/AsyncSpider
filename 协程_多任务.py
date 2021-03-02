# -*- coding: utf-8 -*-
import asyncio
import time

urls = [
    "http://127.0.0.1:5000/gpc",
    "http://127.0.0.1:5000/una",
    "http://127.0.0.1:5000/python"
]


async def get_request(url):
    print("正在请求的url:", url)
    time.sleep(2)  # （堵塞操作2秒）出现了不支持异步模块的对象所以耗时6秒未成功进行异步操作
    print("请求结束:", url)


if __name__ == "__main__":
    start = time.time()
    tasks = []  # 多任务列表
    # 1.创建协程对象
    for url in urls:
        c = get_request(url)
        # 2.创建任务对象
        task = asyncio.ensure_future(c)
        tasks.append(task)
    # 3.创建事件循环对象
    loop = asyncio.get_event_loop()
    # 4.将任务对象注册到事件循环中且开启事件循环
    # loop.run_until_complete(tasks)#循环中不能放列表
    loop.run_until_complete(asyncio.wait(tasks))  # 必须使用wait方法对tasks封装
    print("总耗时:", time.time() - start)
