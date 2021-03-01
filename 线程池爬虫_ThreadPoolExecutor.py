# -*- coding: utf-8 -*-
import requests
from lxml import etree
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from fake_useragent import UserAgent


class QiubaiSpider:
    def __init__(self):
        self.url_temp = "https://www.qiushibaike.com/text/page/{}/"
        self.headers = {
            "User-Agent": UserAgent}

    # url_list
    def get_url_list(self):
        return [self.url_temp.format(i) for i in range(1, 5)]

    # 发送请求，获取响应
    def parse_url(self, url):
        response = requests.get(url, headers=self.headers)
        return response.content.decode()

    # 提取数据
    def get_content_list(self, html_str):
        html = etree.HTML(html_str)
        content_list = []
        # 分组
        div_list = html.xpath("//div[@class='col1 old-style-col1']/div")
        for div in div_list:
            item = dict()
            item["author_name"] = div.xpath(".//div[@class='author clearfix']/a[2]/h2/text()")
            item["author_name"] = item["author_name"][0].strip()
            item["content_href"] = div.xpath(".//a[@class='contentHerf']/@href")
            item["content_img"] = div.xpath(".//div[@class='thumb']/a/img/@src")
            item["content_img"] = item["content_img"][0] if len(item["content_img"]) > 0 else None
            item["god_cmt"] = div.xpath(
                ".//a[@class='indexGodCmt']/div[@class='cmtMain']/div[@class='main-text']/text()")
            item["god_cmt"] = item["god_cmt"][0].strip() if len(item["god_cmt"]) > 0 else None
            content_list.append(item)
        return content_list

    # 保存
    def save_content_list(self, content_list):
        # for i in content_list:
        #     print(i)
        file_path = "糗事百科_线程池爬虫.txt"
        with open(file_path, "a", encoding="utf-8") as f:
            for content in content_list:
                f.write(json.dumps(content, ensure_ascii=False, indent=2))
                f.write("\n")

    # 实现主要逻辑
    def run(self):
        # # 1.url_list
        # url_list = self.get_url_list()
        # # 2.遍历，发送请求，获取响应
        # for url in url_list:
        #     html_str = self.parse_url(url)
        #     # 3.提取数据
        #     content_list = self.get_content_list(html_str)
        #     # 4.保存
        #     self.save_content_list(content_list)

        with ThreadPoolExecutor(max_workers=8) as t:
            # for page in range(1, 15):
            #     obj = t.submit(spider, page)
            #     obj_list.append(obj)
            begin = time.time()
            url_list = self.get_url_list()
            html_str_list = []
            for url in url_list:
                html_str = t.submit(self.parse_url, url)
                html_str_list.append(html_str)
            for future in as_completed(html_str_list):
                data = future.result()
                content_list = self.get_content_list(data)
                self.save_content_list(content_list)
            times = time.time() - begin
            print(times)


if __name__ == '__main__':
    qiubai = QiubaiSpider()
    qiubai.run()
