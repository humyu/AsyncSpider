# -*- coding: utf-8 -*-
import asyncio
import time

import aiohttp
from aiomultiprocess import Pool


"""
aiomultiprocess:aiomultiprocess 将异步 IO 和多进程结合起来了，很好的利用了多核和异步 IO 的优势
"""

async def get(url):
    session = aiohttp.ClientSession()
    response = await session.get(url)
    result = await response.text()
    await session.close()
    return result


async def request():
    url = 'http://httpbin.org/get'
    urls = [url for _ in range(100)]
    async with Pool() as pool:
        result = await pool.map(get, urls)
        return result


if __name__ == '__main__':
    start = time.time()
    coroutine = request()
    task = asyncio.ensure_future(coroutine)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(task)

    end = time.time()
    print('Cost time:', end - start)
