# -*- coding: utf-8 -*-
from lxml import etree
import json
import aiohttp
import asyncio
from setting import db_mongo


class QiubaiSpider:
    def __init__(self):
        self.url_temp = "https://www.qiushibaike.com/text/page/{}/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/86.0.4240.193 Safari/537.36"}

    # url_list
    def get_url_list(self):
        return [self.url_temp.format(i) for i in range(1, 3)]

    # # 发送请求，获取响应
    # def parse_url(self, url):
    #     response = requests.get(url, headers=self.headers)
    #     return response.content.decode()

    # 发送请求，获取响应
    # 使用with语句
    async def parse_url(self, url):
        async with aiohttp.ClientSession() as session:
            async with await session.get(url, headers=self.headers) as response:
                result = await response.text()
                return result

    # 提取数据
    async def get_content_list(self, url):
        html_str = await self.parse_url(url)
        html = etree.HTML(html_str)
        content_list = []
        # 分组
        div_list = html.xpath("//div[@class='col1 old-style-col1']/div")
        for div in div_list:
            item = dict()
            item["author_img"] = div.xpath(".//div[@class='author clearfix']/a[@rel='nofollow']/img/@src")
            item["author_img"] = item["author_img"][0] if len(item["author_img"]) > 0 else None
            item["author_name"] = div.xpath(".//div[@class='author clearfix']/a[2]/h2/text()")
            item["author_name"] = item["author_name"][0].strip()
            item["author_gender"] = div.xpath(".//div[contains(@class,'articleGender')]/@class")
            item["author_gender"] = item["author_gender"][0].split(" ")[-1].replace("Icon", "") if len(
                item["author_gender"]) > 0 else None
            item["author_age"] = div.xpath(".//div[contains(@class,'articleGender')]/text()")
            item["author_age"] = item["author_age"][0] if len(item["author_age"]) > 0 else None
            item["content"] = div.xpath(".//div[@class='content']/span[1]/text()")
            item["content"] = "".join(item["content"]).strip()
            item["content_href"] = div.xpath(".//a[@class='contentHerf']/@href")
            item["content_img"] = div.xpath(".//div[@class='thumb']/a/img/@src")
            item["content_img"] = item["content_img"][0] if len(item["content_img"]) > 0 else None
            item["god_cmt"] = div.xpath(
                ".//a[@class='indexGodCmt']/div[@class='cmtMain']/div[@class='main-text']/text()")
            item["god_cmt"] = item["god_cmt"][0].strip() if len(item["god_cmt"]) > 0 else None
            content_list.append(item)
        return content_list

    # 使用回调函数保存数据
    def save_content_list(self, content_list):
        file_path = "糗事百科_协程爬虫.txt"
        with open(file_path, "a", encoding="utf-8") as f:
            for content in content_list.result():
                f.write(json.dumps(content, ensure_ascii=False, indent=2))
                f.write("\n")

    # 使用回调函数保存数据
    def save_to_db(self, content_list):
        for content in content_list.result():
            db_mongo.DBMongo().process_item(content)

    # 实现主要逻辑
    def main(self):
        # url_list
        url_list = self.get_url_list()
        # tasks = [asyncio.ensure_future(self.get_content_list(url)) for url in url_list]
        tasks = []  # 多任务列表
        # 1.创建协程对象
        for url in url_list:
            c = self.get_content_list(url)
            # 2.创建任务对象
            task = asyncio.ensure_future(c)
            # 使用回调函数保存数据
            task.add_done_callback(self.save_to_db)
            tasks.append(task)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
        print("end")


if __name__ == '__main__':
    qiubai = QiubaiSpider()
    qiubai.main()
