# -*- coding: utf-8 -*-
"""
使用 ProcessPoolExecutor 模块的 submit 函数 和 _base模块的 as_completed 函数
"""
import json
import random
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import requests
from lxml import etree


class ScrapeSpider:
    def __init__(self):
        self.url_temp = "https://ssr1.scrape.center/page/{}"
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'UM_distinctid=17e004b8696638-054f1543e7fd3c-978183a-100200-17e004b8697346', 'DNT': '1',
            'Host': 'ssr1.scrape.center', 'Pragma': 'no-cache', 'Referer': 'https://ssr1.scrape.center/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"', 'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/96.0.4664.45 Safari/537.36'}
        self.proxies = {
            "http": "58.55.231.237:7082"
        }

    # url_list
    def get_url_list(self):
        return [self.url_temp.format(i) for i in range(1, 5)]

    # 发送请求，获取响应
    def parse_url(self, url):
        time.sleep(random.uniform(2, 4))
        response = requests.get(url, headers=self.headers, proxies=self.proxies)
        return response.content.decode()

    # 提取数据
    def crawl_page(self, html_str):
        html = etree.HTML(html_str)
        content_list = []
        # 分组
        div_list = html.xpath("//div[@class='el-card item m-t is-hover-shadow']")
        for div in div_list:
            detail_url = div.xpath("./div/div/div[2]/a/@href")
            detail_url = detail_url[0]
            title = div.xpath("./div/div/div[2]/a/h2/text()")
            title = title[0]
            categories = div.xpath("./div/div/div[2]/div[1]//span/text()")
            categories = ",".join(categories)
            item = {
                "detail_url": detail_url,
                "title": title,
                "categories": categories,
            }
            content_list.append(item)
        return content_list

    # 保存
    def save_to_file(self, content_list):
        file_path = "spider3_1.txt"
        with open(file_path, "a", encoding="utf-8") as f:
            for content in content_list:
                f.write(json.dumps(content, ensure_ascii=False, indent=2))
                f.write("\n")

    # 实现主要逻辑
    def run(self):
        with ProcessPoolExecutor(max_workers=5) as t:
            url_list = self.get_url_list()
            html_str_list = []
            for url in url_list:
                html_str = t.submit(self.parse_url, url)
                html_str_list.append(html_str)
            content_list_list = []
            for future in as_completed(html_str_list):
                html_str = future.result()
                content_list = t.submit(self.crawl_page, html_str)
                content_list_list.append(content_list)
            for future in as_completed(content_list_list):
                content_list = future.result()
                t.submit(self.save_to_file, content_list)


if __name__ == '__main__':
    begin = time.time()
    spider = ScrapeSpider()
    spider.run()
    times = time.time() - begin
    print(times)