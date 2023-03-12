# -*- coding: utf-8 -*-
import asyncio
import json
import sys
import time

import aiofiles
import aiohttp
from aiomultiprocess import Pool
from lxml import etree
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.append("..")

from setting import config

CONCURRENCY = 5

PAGE_NUMBER = 2

MONGO_DB_NAME = 'books'
MONGO_COLLECTION_NAME = 'yanqing'

client = AsyncIOMotorClient(config.MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_NAME]


class AsyncSpider:
    def __init__(self):
        self.url_temp = "https://www.dushu.com/book/1179_{}.html"
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'Hm_lvt_8008bbd51b8bc504162e1a61c3741a9d=1638867392,1640867708; '
                      'Hm_lpvt_8008bbd51b8bc504162e1a61c3741a9d=1640867850',
            'Host': 'www.dushu.com', 'Pragma': 'no-cache', 'Referer': 'https://www.dushu.com/book/1179.html',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"', 'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/96.0.4664.45 Safari/537.36'}
        self.detail_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'Hm_lvt_8008bbd51b8bc504162e1a61c3741a9d=1638867392,1640867708; '
                      'Hm_lpvt_8008bbd51b8bc504162e1a61c3741a9d=1640868345',
            'Host': 'www.dushu.com', 'Pragma': 'no-cache', 'Referer': 'https://www.dushu.com/book/1179.html',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"', 'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/96.0.4664.45 Safari/537.36'}
        self.proxy = "http://39.98.45.168:8081"
        self.semaphore = None
        self.session = None

    async def parse_url(self, url, headers):
        async with self.semaphore:
            try:
                async with await self.session.get(url, headers=headers, proxy=self.proxy, timeout=10) as response:
                    return await response.text()
            except Exception as e:
                print(f"请求异常==》{e}")
                return "disable"

    async def scrape_index(self, page):
        url = self.url_temp.format(page)
        html_str = await self.parse_url(url, self.headers)
        if html_str == "disable":
            return
        html = etree.HTML(html_str)
        # detail_urls = list()
        # 列表页分组
        div_list = html.xpath("//div[@class='bookslist']/ul/li")
        for div in div_list:
            # 详情页地址
            detail_url = div.xpath("./div/h3/a/@href")
            detail_url = detail_url[0] if len(detail_url) > 0 else None
            detail_url = "https://www.dushu.com" + detail_url
            # detail_urls.append(detail_url)
            return detail_url
        # return detail_urls

    async def scrape_detail(self, detail_url):
        # print(f"detail_url:{detail_url}")
        detail_html_str = await self.parse_url(detail_url, self.detail_headers)
        if detail_html_str == "disable":
            return
        detail_html = etree.HTML(detail_html_str)
        # 书名
        title = detail_html.xpath("//div[@class='bookdetails-left']/div[@class='book-title']/h1/text()")
        title = title[0] if len(title) > 0 else "暂缺书名"
        # 价格
        price = detail_html.xpath("//div[@class='bookdetails-left']/div[@class='book-details']//p/span/text()")
        price = price[0].strip() if len(price) > 0 else "暂缺价格"
        # 作者
        writers = detail_html.xpath("//div[@class='bookdetails-left']/div[@class='book-details']//tr[1]/td[2]/text()")
        writers = ",".join(writers).replace(" 著", "") if len(writers) > 0 else "暂缺作者"
        # 出版社
        pub = detail_html.xpath("//div[@class='bookdetails-left']/div[@class='book-details']//tr[2]/td[2]/text()")
        pub = ",".join(pub) if len(pub) > 0 else "暂缺出版社"
        item = {
            "title": title,
            "price": price,
            "writers": writers,
            "pub": pub
        }
        # await self.save_data(item)
        # await self.save_to_file(item)
        return item

    async def save_data(self, data):
        if data:
            return await collection.update_one({
                'title': data.get('title'),
            }, {
                '$set': data,
            }, upsert=True)

    async def save_to_file(self, data):
        file_path = "spider3.txt"
        async with aiofiles.open(file_path, "a+", encoding="utf-8") as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            await f.write("\n")

    async def run(self):
        self.semaphore = asyncio.Semaphore(CONCURRENCY)
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20, ssl=False))
        scrape_index_tasks = [asyncio.create_task(self.scrape_index(page)) for page in range(1, PAGE_NUMBER + 1)]
        detail_urls = await asyncio.gather(*scrape_index_tasks)
        # # 判断 detail_urls 是否为 NoneType
        # if detail_urls is not None:
        #     scrape_detail_tasks = [asyncio.create_task(self.scrape_detail(detail_url)) for detail_url in
        #                            detail_urls[0]]
        #     await asyncio.wait(scrape_detail_tasks)
        # detail_urls = detail_urls[0]
        pool = Pool()
        try:
            items = await pool.map(self.scrape_detail, detail_urls)
            print(items)
        except Exception as e:
            print(f"异步进程池异常==>{e}")
        finally:
            pool.close()
            await self.session.close()



if __name__ == '__main__':
    begin = time.time()
    async_spider = AsyncSpider()
    asyncio.run(async_spider.run())
    print(time.time() - begin)
