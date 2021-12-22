# -*- coding: utf-8 -*-
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from lxml import etree


class QiubaiSpider:
    def __init__(self):
        self.url_temp = "https://www.qiushibaike.com/text/page/{}/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201"}

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
        file_path = "糗事百科_线程池爬虫.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            for content in content_list:
                f.write(json.dumps(content, ensure_ascii=False, indent=2))
                f.write("\n")

    # 实现主要逻辑
    def run(self):

        with ThreadPoolExecutor(max_workers=10) as t:
            url_list = self.get_url_list()
            html_str_list = []
            for url in url_list:
                html_str = t.submit(self.parse_url, url)
                html_str_list.append(html_str)
            content_list_list = []
            for future in as_completed(html_str_list):
                html_str = future.result()
                content_list = t.submit(self.get_content_list, html_str)
                content_list_list.append(content_list)
            for future in as_completed(content_list_list):
                content_list = future.result()
                t.submit(self.save_content_list, content_list)


if __name__ == '__main__':
    begin = time.time()
    qiubai = QiubaiSpider()
    qiubai.run()
    times = time.time() - begin
    print(times)
