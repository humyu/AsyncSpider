# -*- coding: utf-8 -*-
import asyncio

import aiohttp

CONCURRENCY = 5
URL = 'https://www.baidu.com'
semaphore = asyncio.Semaphore(CONCURRENCY)


async def scrape_api(session):
    # 信号量可以控制进入爬取的最大协程数量
    async with semaphore:
        print('scraping', URL)
        async with session.get(URL) as response:
            await asyncio.sleep(1)
            return await response.text()


async def main():
    # 官方建议在程序中使用单个 ClientSession 对象
    async with aiohttp.ClientSession() as session:
        print(f"{session}")
        scrape_index_tasks = [asyncio.ensure_future(scrape_api(session)) for _ in range(50)]
        # await asyncio.gather(*scrape_index_tasks)
        results = await asyncio.wait(scrape_index_tasks)
        # print(results)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
