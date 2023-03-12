# -*- coding: utf-8 -*-
"""
aiomultiprocess 将异步 IO 和多进程结合起来了，很好的利用了多核和异步 IO 的优势
"""
import asyncio
import sys
import time
import os

import aiohttp
from aiomultiprocess import Pool

sys.path.append("..")


async def parse_url(url):
    print(f"{os.getpid()} is running")
    proxy = "http://49.233.173.151:9080"
    async with aiohttp.ClientSession() as session:
        async with await session.get(url, proxy=proxy, timeout=10) as response:
            result = await response.text()
            return result


async def request():
    url = 'http://httpbin.org/get'
    urls = [url for _ in range(20)]
    async with Pool() as pool:
        result = await pool.map(parse_url, urls)
        print(result)


if __name__ == '__main__':
    start = time.time()
    asyncio.run(request())

    end = time.time()
    print('Cost time:', end - start)
