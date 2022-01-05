# -*- coding: utf-8 -*-
import aiohttp
import asyncio
import time

start = time.time()


async def get(url):
    session = aiohttp.ClientSession()  # 实例化Clientsession()对象
    response = await session.get(url)  # 支持get(),post()，params/data,proxy='..'等参数
    result = await response.text()  # text()字符串，json()json类型，read()二进制
    await session.close()  # 关闭资源，使用with语句可以自动释放
    return result


# 使用with语句
async def get_with(url):
    async with aiohttp.ClientSession() as session:
        async with await  session.get(url) as response:
            result = await response.text()
            return result


async def request():
    url = 'http://httpbin.org/get'
    print('Waiting fro ', url)
    # result = await get(url)
    result = await get_with(url)
    print('Get response from ', url, 'Result:', result)


tasks = [asyncio.ensure_future(request()) for _ in range(5)]
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))

end = time.time()
print('Cost time:', end - start)
