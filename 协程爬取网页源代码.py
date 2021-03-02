# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import time

urls = [
    "http://127.0.0.1:5000/gpc",
    "http://127.0.0.1:5000/una",
    "http://127.0.0.1:5000/python"
]


async def get_request(url):
    async with aiohttp.ClientSession() as sess:  # 实例化一个请求对象
        # get/post(url,headers,params/data,proxy="http://ip:port")
        async with await sess.get(url=url) as response:  # 使用get发起请求，返回一个相应对象
            page_text = await response.text()  # text()获取字符串形式的相应数据  read()获取byte类型的响应数据
            return page_text


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
    loop.run_until_complete(asyncio.wait(tasks))  # 必须使用wait方法对tasks封装
    print("总耗时:", time.time() - start)
