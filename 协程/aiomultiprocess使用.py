# -*- coding: utf-8 -*-
"""
aiomultiprocess 将异步 IO 和多进程结合起来了，很好的利用了多核和异步 IO 的优势
"""
import asyncio
import time

import aiohttp
from aiomultiprocess import Pool


async def parse_url(url):
    async with aiohttp.ClientSession() as session:
        async with await session.get(url) as response:
            result = await response.text()
            return result


async def request():
    url = 'https://www.httpbin.org/get'
    urls = [url for _ in range(100)]
    async with Pool() as pool:
        result = await pool.map(parse_url, urls)
        print(result)


if __name__ == '__main__':
    start = time.time()
    asyncio.run(request())

    end = time.time()
    print('Cost time:', end - start)
