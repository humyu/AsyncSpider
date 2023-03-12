# -*- coding: utf-8 -*-
import asyncio
import json
import sys

import aiofiles
import aiohttp
from lxml import etree
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.append("..")

from setting import config

semaphore = asyncio.Semaphore(10)

# MONGO_CONNECTION_STRING = 'mongodb://admin:asdf1234@localhost:27017'
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

    # url_list
    def get_url_list(self):
        return [self.url_temp.format(i) for i in range(1, 2)]

    # 发送请求，获取响应
    # 使用with语句
    async def parse_url(self, url, session):
        async with semaphore:
            try:
                async with await session.get(url, headers=self.headers, proxy=self.proxy, timeout=10) as response:
                    result = await response.text()
                    return result
            except Exception as e:
                print(f"异常==>{e}")
                return "disable"

    # 提取数据
    async def get_content_list(self, url, session):
        print(f"开始 {url}")
        html_str = await self.parse_url(url, session)
        if html_str == "disable":
            return
        html = etree.HTML(html_str)
        content_list = []
        # 分组
        div_list = html.xpath("//div[@class='bookslist']/ul/li")
        for div in div_list:
            item = dict()
            # 详情页地址
            detail_url = div.xpath("./div/h3/a/@href")
            detail_url = detail_url[0] if len(detail_url) > 0 else None
            detail_url = "https://www.dushu.com" + detail_url
            # 书名
            title = div.xpath("./div/h3/a/text()")
            title = title[0] if len(title) > 0 else None
            item["title"] = title
            # 其他信息
            item = await self.get_detail(detail_url, session, item)
            # print(item)
            content_list.append(item)
        print(f"准备保存 {url}")
        await self.save_to_file(content_list)
        # await self.save_to_db(content_list)
        await asyncio.sleep(2)
        print(f"保存 {url}")

    # 获取详情页数据
    async def get_detail(self, detail_url, session, item):
        detail_html_str = await self.parse_url(detail_url, session)
        if detail_html_str == "disable":
            return
        detail_html = etree.HTML(detail_html_str)
        # 价格
        price = detail_html.xpath("//div[@class='book-details-left']/p/span/text()")
        price = price[0].strip() if len(price) > 0 else "暂缺价格"
        item["price"] = price
        # 作者
        writers = detail_html.xpath("//div[@class='book-details-left']//tr[1]/td[2]/text()")
        writers = ",".join(writers).replace(" 著", "") if len(writers) > 0 else "暂缺作者"
        item["writers"] = writers
        # 出版社
        publisher = detail_html.xpath("//div[@class='book-details-left']//tr[2]/td[2]/text()")
        publisher = ",".join(publisher) if len(publisher) > 0 else "暂缺出版社"
        item["publisher"] = publisher
        return item

    async def save_to_file(self, content_list):
        file_path = "spider1.txt"
        async with aiofiles.open(file_path, "a+", encoding="utf-8") as f:
            for content in content_list:
                await f.write(json.dumps(content, ensure_ascii=False, indent=2))
                await f.write("\n")

    async def save_to_db(self, content_list):
        for content in content_list:
            print(f"保存{content}")
            await collection.update_one({
                'title': content.get('title'),
            }, {
                '$set': content,
            }, upsert=True)

    # 实现主要逻辑
    async def main(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=20, ssl=False)) as session:
            # url_list
            url_list = self.get_url_list()
            tasks = [asyncio.create_task(self.get_content_list(url, session)) for url in url_list]
            await asyncio.wait(tasks)
        print("end")


if __name__ == '__main__':
    spider = AsyncSpider()
    asyncio.run(spider.main())
