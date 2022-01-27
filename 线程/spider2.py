# -*- coding: utf-8 -*-
"""
使用 multiprocessing.dummy 所提供的 Pool 函数 创建线程池
"""
import json
import random
import sys
import time
from multiprocessing.dummy import Pool

import requests
from lxml import etree
from retrying import retry

sys.path.append("..")

from handler import retry_handler as rh


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
            "http": "61.216.156.222:60808"
        }

    # url_list
    def get_url_list(self):
        return [self.url_temp.format(i) for i in range(1, 5)]

    # 发送请求，获取响应
    @retry(wait_random_min=1000, wait_random_max=4000, wait_fixed=2000,
           retry_on_result=rh.retry_if_bad_code, retry_on_exception=rh.retry_if_exception)
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
        file_path = "spider2.txt"
        with open(file_path, "a", encoding="utf-8") as f:
            for content in content_list:
                f.write(json.dumps(content, ensure_ascii=False, indent=2))
                f.write("\n")

    # 实现主要逻辑
    def run(self):
        pool = Pool(4)

        url_list = self.get_url_list()
        html_str_list = pool.map(self.parse_url, url_list)
        content_list = pool.map(self.crawl_page, html_str_list)
        pool.map(self.save_to_file, content_list)

        # 调用 join 之前，先调用 close 函数，否则会出错。执行完 close 后不会有新的线程加入到 pool
        pool.close()
        # join 函数等待所有子线程结束
        pool.join()


if __name__ == '__main__':
    begin = time.time()
    spider = ScrapeSpider()
    spider.run()
    times = time.time() - begin
    print(times)
