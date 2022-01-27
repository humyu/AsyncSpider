# -*- coding: utf-8 -*-
"""
1. 使用 threading模块中的 Thread类 创建线程
2. 数据结构：队列
"""
import json
import random
import threading
import time
from queue import Queue

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
        self.detail_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'UM_distinctid=17e004b8696638-054f1543e7fd3c-978183a-100200-17e004b8697346', 'DNT': '1',
            'Host': 'ssr1.scrape.center', 'Pragma': 'no-cache', 'Referer': 'https://ssr1.scrape.center/page/2',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"', 'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-User': '?1', 'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/96.0.4664.45 Safari/537.36'}

        self.url_queue = Queue()
        self.page_queue = Queue()
        self.detail_url_queue = Queue()
        self.detail_queue = Queue()
        self.target_queue = Queue()
        self.proxies = {
            "http": "61.216.156.222:60808"
        }

    # 1.获取分页列表的 url
    def get_url_list(self):
        for i in range(1, 5):
            self.url_queue.put(self.url_temp.format(i))

    # 2.解析分页列表的 url
    def parse_url(self):
        while True:
            time.sleep(random.uniform(1, 4))
            url = self.url_queue.get()
            try:
                response = requests.get(url, headers=self.headers, proxies=self.proxies)
                if response.status_code == 200:
                    self.page_queue.put(response.content.decode())
                else:
                    self.url_queue.put(url)
            except Exception as e:
                print(e)
                self.url_queue.put(url)
            self.url_queue.task_done()

    # 3.根据解析结果得到详情页 url
    def crawl_page(self):
        while True:
            html_str = self.page_queue.get()
            html = etree.HTML(html_str)
            # 分组
            div_list = html.xpath("//div[@class='el-card item m-t is-hover-shadow']")
            for div in div_list:
                detail_url = div.xpath(".//a[@class='name']/@href")
                detail_url = "".join(["https://ssr1.scrape.center", detail_url[0]])
                self.detail_url_queue.put(detail_url)
            self.page_queue.task_done()

    # 4.解析详情页
    def parse_detail_url(self):
        while True:
            time.sleep(random.uniform(1, 4))
            detail_url = self.detail_url_queue.get()
            try:
                response = requests.get(detail_url, headers=self.detail_headers, proxies=self.proxies)
                if response.status_code == 200:
                    self.detail_queue.put(response.content.decode())
                else:
                    self.detail_url_queue.put(detail_url)
            except Exception as e:
                print(e)
                self.detail_url_queue.put(detail_url)
            self.detail_url_queue.task_done()

    # 5.根据解析结果获取目标数据
    def crawl_detail(self):
        while True:
            detail_html_str = self.detail_queue.get()
            detail_html = etree.HTML(detail_html_str)
            name = detail_html.xpath("//div[@class='item el-row']/div[2]/a/h2/text()")
            name = "".join(name)
            categories = detail_html.xpath("//div[@class='item el-row']/div[2]/div[1]//span/text()")
            categories = ",".join(categories)
            origin = detail_html.xpath("//div[@class='item el-row']/div[2]/div[2]/span[1]/text()")
            origin = "".join(origin)
            length = detail_html.xpath("//div[@class='item el-row']/div[2]/div[2]/span[3]/text()")
            length = "".join(length)
            pub_time = detail_html.xpath("//div[@class='item el-row']/div[2]/div[3]/span/text()")
            pub_time = "".join(pub_time)
            item = {
                "name": name,
                "categories": categories,
                "origin": origin,
                "length": length,
                "pub_time": pub_time
            }
            self.target_queue.put(item)
            self.detail_queue.task_done()

    # 6.保存数据
    def save_to_file(self):
        while True:
            content = self.target_queue.get()
            file_path = "spider1.txt"
            with open(file_path, "a+", encoding="utf-8") as f:
                f.write(json.dumps(content, ensure_ascii=False, indent=2))
                f.write("\n")
            self.target_queue.task_done()

    # 实现主要逻辑
    def run(self):
        thread_list = []
        # 1.获取分页列表的 url
        t1 = threading.Thread(target=self.get_url_list)
        thread_list.append(t1)
        # 2.解析分页列表的 url
        for _ in range(4):
            t2 = threading.Thread(target=self.parse_url)
            thread_list.append(t2)
        # 3.根据解析结果得到详情页 url
        t3 = threading.Thread(target=self.crawl_page)
        thread_list.append(t3)
        # 4.解析详情页
        for _ in range(10):
            t4 = threading.Thread(target=self.parse_detail_url)
            thread_list.append(t4)
        # 5.根据解析结果获取目标数据
        t5 = threading.Thread(target=self.crawl_detail)
        thread_list.append(t5)
        # 6.保存数据
        for _ in range(10):
            t6 = threading.Thread(target=self.save_to_file)
            thread_list.append(t6)

        for t in thread_list:
            # 把子线程设置为守护线程，即当主线程结束时，子线程结束。必须在start()之前设置
            t.setDaemon(True)
            t.start()

        for q in [self.url_queue, self.page_queue, self.detail_url_queue, self.detail_queue, self.target_queue]:
            # 等到队列为空，再执行别的操作
            q.join()


if __name__ == '__main__':
    begin = time.time()
    scrape = ScrapeSpider()
    scrape.run()
    print("主线程结束")
    print(time.time() - begin)
