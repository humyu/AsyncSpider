# -*- coding: utf-8 -*-
import asyncio
import time


async def get_request(url):
    print("正在请求的url:", url)
    time.sleep(2)
    print("请求结束:", url)
    return "我是特殊函数的返回值"


# 回调函数的封装
def task_callback(t):  # 参数t：就是该回调函数的调用者(任务对象)
    print("i am task_callback(),参数t:", t)
    print("t.result()返回的是:", t.result())


if __name__ == "__main__":
    c = get_request("www.1.com")  # c就是一个协程对象

    task = asyncio.ensure_future(c)  # task就是一个任务对象，它是对协程对象的进一步封装
    task.add_done_callback(task_callback)  # 给task绑定一个回调函数

    loop = asyncio.get_event_loop()  # loop就是一个事件循环对象

    loop.run_until_complete(task)  # 将任务对象注册到事件循环中且开启事件循环

    print("主函数结束!")
